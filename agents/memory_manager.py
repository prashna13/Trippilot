from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext


def remember_preference(key: str, value: str, tool_context: ToolContext) -> str:
    """Stores a user preference (e.g. preferred_airline, hotel_chain) in user-scoped memory."""
    tool_context.state[f"user:{key}"] = value
    tool_context.add_memory(f"User preference: {key} = {value}")
    return f"Saved preference: {key} = {value}"


def recall_preference(key: str, tool_context: ToolContext) -> str:
    """Retrieves a previously stored user preference by key."""
    val = tool_context.state.get(f"user:{key}")
    if val is not None:
        return f"{key}: {val}"
    return f"No preference found for '{key}'."


async def search_user_memories(query: str, tool_context: ToolContext) -> str:
    """Searches across all user memories (previous trips, preferences) using a keyword query."""
    results = await tool_context.search_memory(query=query)
    if not results.memories:
        return f"No memories found matching '{query}'."
    lines = []
    for m in results.memories:
        if m.content and m.content.parts:
            lines.append(f"- {m.author}: {m.content.parts[0].text}")
    return "Memories found:\n" + "\n".join(lines)


remember_tool = FunctionTool(func=remember_preference)
recall_tool = FunctionTool(func=recall_preference)
search_memories_tool = FunctionTool(func=search_user_memories)
