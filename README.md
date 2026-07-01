# TripPilot

TripPilot is a multi-agent AI travel concierge that helps users plan, search real flights/hotels, and execute sandbox bookings based on natural language inputs.

## Project Structure

```
trippilot/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
└── agents/
    ├── __init__.py
    ├── root_agent.py
    └── planner_agent.py
```

- **`main.py`**: Entrypoint exposing the FastAPI web server.
- **`agents/`**: Contains Google ADK agent definitions.
  - **`root_agent.py`**: User-facing coordinator agent that delegates tasks to other specialists.
  - **`planner_agent.py`**: Agent responsible for creating travel itineraries and structured briefs.

## Setup & Local Run

1. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Copy `.env.example` to `.env` and set your API key:
   ```env
   GEMINI_API_KEY=AIzaSy...
   ```

4. **Run FastAPI Server**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Interact via API**:
   You can make POST requests to the `/chat` endpoint:
   ```bash
   curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "I want to go to Tokyo from Dec 1 to Dec 10 with a budget of $2500"}'
   ```
