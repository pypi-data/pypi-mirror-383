import asyncio

from langgraph.checkpoint.memory import MemorySaver
from rich import print
from universal_mcp.agentr.registry import AgentrRegistry

from universal_mcp.agents.unified import UnifiedAgent
from universal_mcp.agents.utils import messages_to_list


async def main():
    memory = MemorySaver()
    default_tools = {"llm": ["generate_text", "classify_data", "extract_data", "call_llm"]}
    agent = UnifiedAgent(
        name="CodeAct Agent",
        instructions="Be very concise in your answers.",
        model="anthropic:claude-4-sonnet-20250514",
        tools=default_tools,
        registry=AgentrRegistry(),
        memory=memory,
    )
    print("Starting agent...")
    result = await agent.invoke(user_input="find the 80th fibonnaci number")
    print(messages_to_list(result["messages"]))


if __name__ == "__main__":
    asyncio.run(main())
