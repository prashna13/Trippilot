import os
import sys
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

MCP_SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_server.py")

_search_args = [MCP_SERVER_SCRIPT]
if sys.executable and os.path.exists(sys.executable):
    _search_args = [sys.executable, MCP_SERVER_SCRIPT]

search_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=_search_args[0],
            args=_search_args[1:] if len(_search_args) > 1 else [],
        ),
        timeout=30,
    ),
)

search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are the TripPilot Search Specialist. Your job is to find real-time "
        "flight and hotel options using the MCP tools available to you.\n\n"
        "Follow these instructions:\n"
        "1. You have MCP tools: 'search_flights', 'search_hotels', 'create_booking'.\n"
        "2. When given a trip brief with destination, dates, and budget, use search_flights "
        "and search_hotels to find options.\n"
        "3. Present the results in a readable ranked format (by price).\n"
        "4. If the user asks to book a specific flight, use create_booking.\n"
        "5. Return 'NO_FLIGHTS' if no flights match, 'NO_HOTELS' if no hotels match."
    ),
    tools=[search_toolset],
)
