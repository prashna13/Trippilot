from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from agents.search_agent import search_agent
from agents.itinerary_builder import itinerary_tool
from agents.memory_manager import remember_tool, recall_tool, search_memories_tool
from agents.model_config import get_main_model

search_tool = AgentTool(agent=search_agent)

planner_agent = Agent(
    name="planner_agent",
    model=get_main_model(),
    instruction=(
        "You are a Travel Planner Agent. You MUST call tools in order. Do NOT make up data.\n\n"
        "Mandatory steps:\n"
        "1. Call 'recall_preference' for 'preferred_destination', 'preferred_airline', 'preferred_budget'.\n"
        "2. If the user mentions preferences, call 'remember_preference' to store them.\n"
        "3. Call the 'search_agent' tool with destination, dates, and budget to find real flights and hotels. "
        "You MUST use the search_agent — do not invent flight or hotel data yourself.\n"
        "4. Call 'build_itinerary' with destination, dates, budget, and the search results.\n"
        "5. Return the build_itinerary JSON result to the user.\n\n"
        "CRITICAL: Never make up flights, hotels, prices, or activities. Always use the tools."
    ),
    tools=[search_tool, itinerary_tool, remember_tool, recall_tool, search_memories_tool],
)
