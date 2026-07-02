from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from agents.planner_agent import planner_agent
from agents.booking_agent import booking_agent
from agents.model_config import get_main_model

planner_tool = AgentTool(agent=planner_agent)
booking_tool = AgentTool(agent=booking_agent)

root_agent = Agent(
    name="root_agent",
    model=get_main_model(),
    instruction=(
        "You are a TripPilot travel concierge.\n\n"
        "Extraction rules:\n"
        "- Scan for dollar amounts ($2000, '2000 dollars', 'budget 1500'). These are budgets.\n"
        "- If destination, dates, and budget are all present, delegate immediately to 'planner_agent'.\n"
        "- If some are missing, ask only for what's missing.\n\n"
        "Booking rule (CRITICAL):\n"
        "When the user mentions booking a flight or says 'book' in any context, you MUST "
        "delegate to 'booking_agent' immediately. Do NOT discuss flight options, do NOT ask which "
        "flight — just hand off to booking_agent with whatever flight context the user provided.\n"
        "NEVER handle booking logic yourself.\n\n"
        "When planner_agent returns the brief, output it to the user."
    ),
    tools=[planner_tool, booking_tool]
)
