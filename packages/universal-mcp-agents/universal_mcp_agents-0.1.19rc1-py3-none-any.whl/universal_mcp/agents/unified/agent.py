import json
import re
from typing import Literal, cast

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_core.tools import tool as create_tool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import START, StateGraph
from langgraph.types import Command, RetryPolicy
from loguru import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.utils import convert_tool_ids_to_dict, filter_retry_on, get_message_text

from .llm_tool import smart_print
from .prompts import (
    PLAYBOOK_CONFIRMING_PROMPT,
    PLAYBOOK_GENERATING_PROMPT,
    PLAYBOOK_PLANNING_PROMPT,
    create_default_prompt,
)
from .sandbox import eval_unsafe
from .state import CodeActState
from .tools import create_meta_tools, enter_playbook_mode, get_valid_tools
from .utils import inject_context, smart_truncate


class UnifiedAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        tools: ToolConfig | None = None,
        registry: ToolRegistry | None = None,
        playbook_registry: object | None = None,
        sandbox_timeout: int = 20,
        **kwargs,
    ):
        super().__init__(
            name=name,
            instructions=instructions,
            model=model,
            memory=memory,
            **kwargs,
        )
        self.model_instance = load_chat_model(model)
        self.tools_config = tools or {}
        self.registry = registry
        self.playbook_registry = playbook_registry
        self.sandbox_timeout = sandbox_timeout
        self.eval_fn = eval_unsafe
        if self.tools_config and not self.registry:
            raise ValueError("Registry must be provided with tools")

    async def _build_graph(self):  # noqa: PLR0915
        meta_tools = create_meta_tools(self.registry)
        additional_tools = [smart_print, meta_tools["web_search"]]
        self.additional_tools = [t if isinstance(t, StructuredTool) else create_tool(t) for t in additional_tools]
        self.default_tools = await self.registry.export_tools(self.tools_config, ToolFormat.LANGCHAIN)

        async def call_model(state: CodeActState) -> Command[Literal["sandbox", "execute_tools"]]:
            self.exported_tools = []

            selected_tool_ids = state.get("selected_tool_ids", [])
            self.exported_tools = await self.registry.export_tools(selected_tool_ids, ToolFormat.LANGCHAIN)
            all_tools = self.exported_tools + self.additional_tools
            self.final_instructions, self.tools_context = create_default_prompt(all_tools, self.instructions)
            messages = [{"role": "user", "content": self.final_instructions}] + state["messages"]

            if state.get("output"):
                messages.append(
                    {
                        "role": "system",
                        "content": f"The last code execution resulted in this output:\n{state['output']}",
                    }
                )

            # Run the model and potentially loop for reflection
            model_with_tools = self.model_instance.bind_tools(
                tools=[
                    enter_playbook_mode,
                    meta_tools["search_functions"],
                    meta_tools["load_functions"],
                ],
                tool_choice="auto",
            )
            response = cast(AIMessage, model_with_tools.invoke(messages))
            response_text = get_message_text(response)
            code_match = re.search(r"```python\n(.*?)\n```", response_text, re.DOTALL)

            if code_match:
                code = code_match.group(1).strip()
                return Command(goto="sandbox", update={"messages": [response], "code": code, "output": ""})
            elif response.tool_calls:
                return Command(goto="execute_tools", update={"messages": [response]})
            else:
                return Command(update={"messages": [response]})

        async def execute_tools(state: CodeActState) -> Command[Literal["call_model", "playbook", "sandbox"]]:
            """Execute tool calls"""
            last_message = state["messages"][-1]
            tool_calls = last_message.tool_calls if isinstance(last_message, AIMessage) else []

            tool_messages = []
            new_tool_ids = []
            ask_user = False
            ai_msg = ""
            tool_result = ""

            for tool_call in tool_calls:
                try:
                    if tool_call["name"] == "enter_playbook_mode":
                        tool_message = ToolMessage(
                            content=json.dumps("Entered Playbook Mode."),
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"],
                        )
                        return Command(
                            goto="playbook",
                            update={"playbook_mode": "planning", "messages": [tool_message]},  # Entered Playbook mode
                        )
                    elif tool_call["name"] == "load_functions":  # Handle load_functions separately
                        valid_tools, unconnected_links = await get_valid_tools(
                            tool_ids=tool_call["args"]["tool_ids"], registry=self.registry
                        )
                        new_tool_ids.extend(valid_tools)
                        # Create tool message response
                        tool_result = f"Successfully loaded {len(valid_tools)} tools: {valid_tools}"
                        links = "\n".join(unconnected_links)
                        if links:
                            ask_user = True
                            ai_msg = f"Please login to the following app(s) using the following links and let me know in order to proceed:\n {links} "
                    elif tool_call["name"] == "search_functions":
                        tool_result = await meta_tools["search_functions"].ainvoke(tool_call["args"])
                except Exception as e:
                    tool_result = f"Error during {tool_call}: {e}"

                tool_message = ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
                tool_messages.append(tool_message)

            if ask_user:
                tool_messages.append(AIMessage(content=ai_msg))
                return Command(update={"messages": tool_messages, "selected_tool_ids": new_tool_ids})

            return Command(goto="call_model", update={"messages": tool_messages, "selected_tool_ids": new_tool_ids})

        def sandbox(state: CodeActState) -> Command[Literal["call_model"]]:
            code = state.get("code")

            if not code:
                logger.error("Sandbox called without code")
                return Command(
                    goto="call_model",
                    update={"output": "Sandbox was called without any code to execute."},
                )

            previous_add_context = state.get("add_context", {})
            add_context = inject_context(previous_add_context, self.tools_context)
            existing_context = state.get("context", {})
            context = {**existing_context, **add_context}
            # Execute the script in the sandbox

            output, new_context, new_add_context = self.eval_fn(
                code, context, previous_add_context, 180
            )  # default timeout 3 min
            output = smart_truncate(output)

            return Command(
                goto="call_model",
                update={
                    "output": output,
                    "code": "",
                    "context": new_context,
                    "add_context": new_add_context,
                },
            )

        def playbook(state: CodeActState) -> Command[Literal["call_model"]]:
            playbook_mode = state.get("playbook_mode")
            if playbook_mode == "planning":
                planning_instructions = self.instructions + PLAYBOOK_PLANNING_PROMPT
                messages = [{"role": "system", "content": planning_instructions}] + state["messages"]

                response = self.model_instance.invoke(messages)
                response = cast(AIMessage, response)
                response_text = get_message_text(response)
                # Extract plan from response text between triple backticks
                plan_match = re.search(r"```(.*?)```", response_text, re.DOTALL)
                if plan_match:
                    plan = plan_match.group(1).strip()
                else:
                    plan = response_text.strip()
                return Command(update={"messages": [response], "playbook_mode": "confirming", "plan": plan})

            elif playbook_mode == "confirming":
                confirmation_instructions = self.instructions + PLAYBOOK_CONFIRMING_PROMPT
                messages = [{"role": "system", "content": confirmation_instructions}] + state["messages"]
                response = self.model_instance.invoke(messages, stream=False)
                response = get_message_text(response)
                if "true" in response.lower():
                    return Command(goto="playbook", update={"playbook_mode": "generating"})
                else:
                    return Command(goto="playbook", update={"playbook_mode": "planning"})

            elif playbook_mode == "generating":
                generating_instructions = self.instructions + PLAYBOOK_GENERATING_PROMPT
                messages = [{"role": "system", "content": generating_instructions}] + state["messages"]
                response = cast(AIMessage, self.model_instance.invoke(messages))
                raw_content = get_message_text(response)
                func_code = raw_content.strip()
                func_code = func_code.replace("```python", "").replace("```", "")
                func_code = func_code.strip()

                # Extract function name (handle both regular and async functions)
                match = re.search(r"^\s*(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", func_code, re.MULTILINE)
                if match:
                    function_name = match.group(1)
                else:
                    function_name = "generated_playbook"

                # Save or update an Agent using the helper registry
                saved_note = ""
                try:
                    if not self.playbook_registry:
                        raise ValueError("Playbook registry is not configured")

                    # Build instructions payload embedding the plan and function code
                    instructions_payload = {
                        "playbookPlan": state["plan"],
                        "playbookScript": {
                            "name": function_name,
                            "code": func_code,
                        },
                    }

                    # Convert tool ids list to dict
                    tool_dict = convert_tool_ids_to_dict(state["selected_tool_ids"])

                    res = self.playbook_registry.create_agent(
                        name=function_name,
                        description=f"Generated playbook: {function_name}",
                        instructions=instructions_payload,
                        tools=tool_dict,
                        visibility="private",
                    )
                    saved_note = f"Successfully created your playbook! Check it out here: [View Playbook](https://wingmen.info/agents/{res.id})"
                except Exception as e:
                    saved_note = f"Failed to save generated playbook as Agent '{function_name}': {e}"

                # Mock tool call for exit_playbook_mode (for testing/demonstration)
                mock_exit_tool_call = {"name": "exit_playbook_mode", "args": {}, "id": "mock_exit_playbook_123"}
                mock_assistant_message = AIMessage(content=saved_note, tool_calls=[mock_exit_tool_call])

                # Mock tool response for exit_playbook_mode
                mock_exit_tool_response = ToolMessage(
                    content=json.dumps(f"Exited Playbook Mode.{saved_note}"),
                    name="exit_playbook_mode",
                    tool_call_id="mock_exit_playbook_123",
                )

                return Command(
                    update={"messages": [mock_assistant_message, mock_exit_tool_response], "playbook_mode": "normal"}
                )

        def route_entry(state: CodeActState) -> Literal["call_model", "playbook"]:
            """Route to either normal mode or playbook creation"""
            if state.get("playbook_mode") in ["planning", "confirming", "generating"]:
                return "playbook"

            return "call_model"

        agent = StateGraph(state_schema=CodeActState)
        agent.add_node(call_model, retry_policy=RetryPolicy(max_attempts=3, retry_on=filter_retry_on))
        agent.add_node(sandbox)
        agent.add_node(playbook)
        agent.add_node(execute_tools)
        agent.add_conditional_edges(START, route_entry)
        # agent.add_edge(START, "call_model")
        return agent.compile(checkpointer=self.memory)
