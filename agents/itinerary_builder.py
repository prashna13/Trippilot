import json
from typing import Any
from google.genai import types
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.adk.memory.memory_entry import MemoryEntry


async def build_itinerary(
    destination: str,
    dates: str,
    budget: str,
    flights: list[dict[str, Any]] | None = None,
    hotels: list[dict[str, Any]] | None = None,
    tool_context: ToolContext | None = None,
) -> str:
    """Assembles a structured trip itinerary from destination, dates, budget, and optional flight/hotel results. Saves the brief to session state."""
    flights = flights or []
    hotels = hotels or []

    brief = {
        "destination": destination,
        "dates": dates,
        "budget": budget,
        "flights": flights,
        "hotels": hotels,
        "recommendation": "",
    }

    total_flight_cost = sum(f.get("price", 0) for f in flights)
    total_hotel_cost = sum(h.get("price_per_night", 0) for h in hotels)
    brief["recommendation"] = f"Total flight cost: ${total_flight_cost}, hotel from ${total_hotel_cost}/night."

    brief_json = json.dumps(brief, indent=2)

    if tool_context:
        tool_context.state["app:trip_brief"] = brief
        tool_context.state["app:flights"] = flights
        tool_context.state["app:hotels"] = hotels

        await tool_context.add_memory(
            memories=[MemoryEntry(
                content=types.Content(
                    parts=[types.Part(text=f"User planned trip to {destination} on {dates} with budget {budget}")]
                )
            )]
        )

    return brief_json


itinerary_tool = FunctionTool(func=build_itinerary)
