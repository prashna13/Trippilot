# TripPilot Agentic Developer Guide

This guide establishes the rules, architecture, and phase-by-phase roadmap for developing TripPilot. Any agent working on this repository MUST strictly follow these rules and context.

## Non-negotiable Rules
1. **Phase Constraint**: NEVER build more than one phase in a single pass. Complete only the phase currently marked [ACTIVE], then stop.
2. **Phase Report**: At the end of every phase, produce a short "Phase Report" containing:
   - What was built (files touched, key decisions made)
   - Which 5-Day Agents Intensive concept(s) this phase demonstrates, and how (be specific)
   - Assumptions made
   - Open questions or trade-offs
3. **Approval Gate**: Do not start the next phase until the user replies with explicit approval (e.g. "approved, continue").
4. **Runnable State**: Every phase must leave the project in a runnable, working state. Never commit half-finished code that breaks the app.
5. **No Secrets**: Never hardcode secrets, API keys, or credentials anywhere. Use `.env` and `.env.example`.
6. **Code Documentation**: Comment code to explain *why*, not just what, especially around agent orchestration and tool decisions.
7. **Ask on Ambiguity**: If a phase's scope is ambiguous, ask the user one clarifying question rather than guessing.

---

## Project Context & Tech Stack
- **Track**: Concierge Agents
- **Core Idea**: Natural language trip goal → agent planning → search real flight/hotel inventory → execute sandbox booking after explicit user confirmation.
- **Stack**: Python 3.12+, FastAPI, Google ADK (Agent Development Kit), MCP server, Amadeus sandbox API, Cloud Run.
- **Model**: Gemini (e.g., `gemini-2.5-flash` or as configured).

---

## Repository Structure & Architecture
```
trippilot/
├── .env.example
├── .gitignore
├── Dockerfile
├── .dockerignore
├── README.md
├── requirements.txt
├── main.py
└── agents/
    ├── __init__.py
    ├── root_agent.py
    ├── planner_agent.py
    ├── search_agent.py (Phase 2+)
    └── booking_agent.py (Phase 4+)
```

- **Root/Orchestrator Agent**: Handles the user conversation, coordinates other agents.
- **Planner Agent**: Assembles and manages itineraries, budget allocation (Phase 3) [ACTIVE].
- **Search Agent**: Connects to the MCP server for real-time inventory (Phase 2) [COMPLETE].
- **Itinerary Builder**: Reusable skill/tool assembling structured trip briefs (Phase 3) [COMPLETE].
- **Memory Manager**: Tools for user preference storage and cross-session recall (Phase 3) [COMPLETE].
- **Booking Agent**: Performs sandbox booking after explicit user confirmation (Phase 4) [COMPLETE].

---

## Roadmap

### Phase 1 — Foundations: first agent + first multi-agent system [COMPLETE]
- Scaffold repo structure.
- Build a single Root Agent using Google ADK powered by Gemini, holding conversation and echoing back a structured trip request brief (destination, dates, budget).
- Delegate to a stub Planner Agent to prove agent-to-agent delegation works.
- Deliverable: Backend runs locally, conversational API produces structured trip brief.

### Phase 2 — Tools & Interoperability: MCP server + external API [COMPLETE]
- Implement MCP server exposing search_flights, search_hotels, create_booking.
- Connect flights/hotels search to Amadeus sandbox API.
- Create Search Agent connected to MCP tools.
- Handoff: Root → Planner → Search → Root with ranked results.

### Phase 3 — Context Engineering: memory, sessions, skills [COMPLETE]
- Add session state remembering trip brief and search results.
- Implement itinerary-assembly logic in Planner Agent as a reusable "skill".
- Add lightweight long-term memory for user preferences (privacy-conscious).
- Trim context/token usage between agents.

### Phase 4 — Quality & Security: guardrails, evals, threat mitigation [COMPLETE]
- Implement Booking Agent with hard guardrail requiring explicit user confirmation in current turn.
- Add basic evaluations test set.
- Add guardrails against prompt injection.

### Phase 5 — Prototype to Production: deployment & observability [ACTIVE]
- Dockerize backend.
- Deploy to Cloud Run with Secret Manager.
- Add structured logging and observability.
