import json
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext


def _has_explicit_confirmation(tool_context: ToolContext, **kwargs) -> bool:
    user_msg = (tool_context.user_content.parts[0].text or "").lower()
    confirm_phrases = ["i confirm", "yes", "book it", "book now", "go ahead", "confirm"]
    return any(phrase in user_msg for phrase in confirm_phrases)


async def create_booking(
    flight_offer: str,
    traveler_name: str,
    tool_context: ToolContext,
) -> str:
    """Books a flight after user confirmation. Requires explicit 'I confirm' or 'Yes' from the user in the same turn."""
    return json.dumps({
        "status": "confirmed",
        "booking_reference": "MOCK-BKG-" + str(hash(traveler_name))[-6:],
        "flight": flight_offer,
        "traveler": traveler_name,
        "message": "Booking confirmed. Enjoy your trip!",
    }, indent=2)


booking_tool = FunctionTool(
    func=create_booking,
    require_confirmation=_has_explicit_confirmation,
)

booking_agent = Agent(
    name="booking_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are the TripPilot Booking Specialist. You handle flight booking confirmation.\n\n"
        "STRICT RULES:\n"
        "1. NEVER book a flight without explicit user confirmation in the SAME conversation turn.\n"
        "2. When the user requests a booking, first summarize what will be booked.\n"
        "3. Ask them to confirm by saying 'I confirm' or 'Yes'.\n"
        "4. Only then call the 'create_booking' tool.\n"
        "5. If the user refuses or is unsure, DO NOT book. Inform them the booking was not made."
    ),
    tools=[booking_tool],
)
