import json
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from agents.model_config import get_main_model


def _has_explicit_confirmation(tool_context: ToolContext, **kwargs) -> bool:
    user_msg = (tool_context.user_content.parts[0].text or "").lower()
    confirm_phrases = ["i confirm", "yes", "book it", "book now", "go ahead", "confirm"]
    return any(phrase in user_msg for phrase in confirm_phrases)


async def create_booking(
    flight_offer: str,
    traveler_name: str = "Guest Traveler",
    tool_context: ToolContext | None = None,
) -> str:
    """Books a flight after user confirmation. Requires explicit 'I confirm' or 'Yes' from the user in the same turn."""
    name = traveler_name or "Guest Traveler"
    return json.dumps({
        "status": "confirmed",
        "booking_reference": "MOCK-BKG-" + str(hash(name))[-6:],
        "flight": flight_offer,
        "traveler": name,
        "message": "Booking confirmed. Enjoy your trip!",
    }, indent=2)


booking_tool = FunctionTool(
    func=create_booking,
    require_confirmation=_has_explicit_confirmation,
)

booking_agent = Agent(
    name="booking_agent",
    model=get_main_model(),
    instruction=(
        "You are the TripPilot Booking Specialist.\n\n"
        "STRICT RULES:\n"
        "1. When the user confirms, IMMEDIATELY call the 'create_booking' tool with the flight details "
        "and traveler name. If the traveler name is not available, use 'Guest Traveler' as a placeholder.\n"
        "2. Do NOT ask for traveler details. Call the tool now.\n"
        "3. If the user refuses or is unsure, DO NOT book."
    ),
    tools=[booking_tool],
)
