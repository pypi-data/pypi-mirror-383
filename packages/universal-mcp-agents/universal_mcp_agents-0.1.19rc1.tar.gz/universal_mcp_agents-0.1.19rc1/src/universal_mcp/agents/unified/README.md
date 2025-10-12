# Unified Agent

The Unified Agent is a sophisticated AI assistant designed to understand and execute tasks by writing and running Python code. It operates within a secure sandbox environment and can leverage a variety of tools to interact with external systems and perform complex operations. A key feature of the Unified Agent is its ability to create reusable "playbooks" from user workflows, enabling automation of repeated tasks.

## Architecture

The agent's architecture is built upon the LangGraph library, creating a state machine that cycles between thinking (calling a language model) and acting (executing code or tools).

### Core Components:

*   **`UnifiedAgent`**: The fundamental agent implementation. It processes user requests, writes Python code, and executes it in a sandbox to achieve the desired outcome. It also has a "playbook mode" to generate reusable Python functions from a user's workflow.
*   **State Graph (`CodeActState`)**: The agent's logic is defined as a state graph. The primary nodes are:
    *   `call_model`: Invokes the language model to generate Python code or select a tool based on the current state and user input.
    *   `sandbox`: Executes the generated Python code using a safe `eval` function with a timeout. The results and any errors are captured and fed back into the state.
    *   `execute_tools`: Handles the execution of meta-tools for searching, loading, and interacting with external functions.
    *   `playbook`: Manages the playbook creation process, including planning, user confirmation, and code generation.
*   **Sandbox (`sandbox.py`)**: A secure execution environment that runs Python code in a separate thread with a timeout. It ensures that the agent's code execution is isolated and cannot harm the host system.
*   **Tools**: The agent has access to a set of powerful tools:
    *   `execute_ipython_cell`: The primary tool for executing arbitrary Python code snippets.
    *   **AI Functions (`llm_tool.py`)**: A suite of functions (`generate_text`, `classify_data`, `extract_data`, `call_llm`) that allow the agent to delegate complex reasoning, classification, and data extraction tasks to a language model.
    *   **Meta Tools (`tools.py`)**: Functions like `search_functions` and `load_functions` that enable the agent to dynamically discover and load new tools from a `ToolRegistry`.

## Playbook Mode

A key feature of the Unified Agent is its ability to create reusable "playbooks". When a user performs a task that they might want to repeat in the future, they can trigger the playbook mode. The agent will then:

1.  **Plan:** Analyze the workflow and create a step-by-step plan for a reusable function, identifying user-specific variables that should become function parameters.
2.  **Confirm:** Ask the user for confirmation of the generated plan.
3.  **Generate:** Generate a Python function based on the confirmed plan. This function can be saved and executed later to automate the task.

## Getting Started (`__main__.py`)

The `__main__.py` file serves as a simple command-line interface for interacting with the agent. It demonstrates how to instantiate the `UnifiedAgent`, configure it with tools, and invoke it with a user request. This allows for easy testing and experimentation with the agent's capabilities.

To run the agent, execute the following command from the root of the repository:
```bash
uv run python -m src.universal_mcp.agents.unified.__main__
```

Major TODO:
- [] Improve LLM Tools
    - [] Use smaller dedicated models for universal_write, clasify etc
- Improve Sandbox
    - [] Support saving loading context
    - [] Direct async tool support
