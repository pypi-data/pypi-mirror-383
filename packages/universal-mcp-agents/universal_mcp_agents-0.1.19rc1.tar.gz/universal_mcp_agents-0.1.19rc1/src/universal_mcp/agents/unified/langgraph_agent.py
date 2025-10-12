from universal_mcp.agentr.registry import AgentrRegistry

from universal_mcp.agents.unified import UnifiedAgent


async def agent():
    agent_obj = UnifiedAgent(
        name="CodeAct Agent",
        instructions="Be very concise in your answers.",
        model="anthropic:claude-4-sonnet-20250514",
        tools=[],
        registry=AgentrRegistry(),
    )
    return await agent_obj._build_graph()
