from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from agents.search_agent import search_agent
from agents.itinerary_builder import itinerary_tool
from agents.memory_manager import remember_tool, recall_tool, search_memories_tool

search_tool = AgentTool(agent=search_agent)

planner_agent = Agent(
    name="planner_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a specialized Travel Planner Agent. Your job is to take the extracted travel details "
        "(destination, dates, budget) and assemble a complete trip plan.\n\n"
        "Follow these steps in order:\n"
        "1. First, check if the user has any stored preferences by calling 'recall_preference' "
        "for 'preferred_destination', 'preferred_airline', 'preferred_budget'.\n"
        "2. If the user mentions preferences (e.g. 'I prefer Delta airlines'), call "
        "'remember_preference' to store them.\n"
        "3. Call the 'search_agent' tool with a message containing the destination, dates, and budget "
        "to find flights and hotels.\n"
        "4. Call 'build_itinerary' with the destination, dates, budget, and search results "
        "to assemble the structured trip brief.\n"
        "5. Return the JSON result from build_itinerary to the user.\n\n"
        "The 'build_itinerary' tool automatically saves the trip to session state and memory."
    ),
    tools=[search_tool, itinerary_tool, remember_tool, recall_tool, search_memories_tool],
)
