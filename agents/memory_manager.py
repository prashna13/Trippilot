from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

_MEMORIES_KEY = "user:_memories"


def remember_preference(key: str, value: str, tool_context: ToolContext) -> str:
    """Stores a user preference in state and appends to the memory list."""
    tool_context.state[f"user:{key}"] = value
    memories: list = tool_context.state.get(_MEMORIES_KEY, [])
    entry = f"User preference: {key} = {value}"
    if entry not in memories:
        memories.append(entry)
        tool_context.state[_MEMORIES_KEY] = memories
    return f"Saved preference: {key} = {value}"


def recall_preference(key: str, tool_context: ToolContext) -> str:
    """Retrieves a previously stored user preference by key."""
    val = tool_context.state.get(f"user:{key}")
    if val is not None:
        return f"{key}: {val}"
    return f"No preference found for '{key}'."


def search_user_memories(query: str, tool_context: ToolContext) -> str:
    """Searches across saved memory entries in state using a keyword query."""
    memories: list = tool_context.state.get(_MEMORIES_KEY, [])
    query_lower = query.lower()
    matches = [m for m in memories if query_lower in m.lower()]
    if not matches:
        return f"No memories found matching '{query}'."
    return "Memories found:\n" + "\n".join(f"- {m}" for m in matches)


remember_tool = FunctionTool(func=remember_preference)
recall_tool = FunctionTool(func=recall_preference)
search_memories_tool = FunctionTool(func=search_user_memories)
