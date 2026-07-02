import json
from typing import Any
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

_MEMORIES_KEY = "user:_memories"


async def build_itinerary(
    destination: str,
    dates: str,
    budget: str,
    flights: list[dict[str, Any]] | None = None,
    hotels: list[dict[str, Any]] | None = None,
    tool_context: ToolContext | None = None,
) -> str:
    """Assembles a structured trip itinerary from destination, dates, budget, and optional flight/hotel results. Saves the brief to session state."""
    if isinstance(flights, str) or not isinstance(flights, list):
        flights = []
    if isinstance(hotels, str) or not isinstance(hotels, list):
        hotels = []

    brief = {
        "destination": destination,
        "dates": dates,
        "budget": budget,
        "flights": flights,
        "hotels": hotels,
        "recommendation": "",
    }

    total_flight_cost = sum(f.get("price", 0) for f in flights if isinstance(f, dict))
    total_hotel_cost = sum(h.get("price_per_night", 0) for h in hotels if isinstance(h, dict))
    brief["recommendation"] = f"Total flight cost: ${total_flight_cost}, hotel from ${total_hotel_cost}/night."

    brief_json = json.dumps(brief, indent=2)

    if tool_context:
        tool_context.state["app:trip_brief"] = brief
        tool_context.state["app:flights"] = flights
        tool_context.state["app:hotels"] = hotels

        memories: list = tool_context.state.get(_MEMORIES_KEY, [])
        entry = f"User planned trip to {destination} on {dates} with budget {budget}"
        if entry not in memories:
            memories.append(entry)
            tool_context.state[_MEMORIES_KEY] = memories

    return brief_json


itinerary_tool = FunctionTool(func=build_itinerary)
