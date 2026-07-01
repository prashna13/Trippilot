import os
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("trippilot.mcp_server")

server = Server("trippilot", version="1.0.0")

try:
    from amadeus import Client, ResponseError
    _amadeus_client = None
    client_id = os.getenv("AMADEUS_CLIENT_ID")
    client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
    if client_id and client_secret:
        _amadeus_client = Client(client_id=client_id, client_secret=client_secret, hostname="test")
        logger.info("Amadeus client initialized (sandbox mode)")
    else:
        logger.warning("AMADEUS_CLIENT_ID/AMADEUS_CLIENT_SECRET not set; using mock data")
except ImportError:
    logger.warning("amadeus package not installed; using mock data")
    _amadeus_client = None
    ResponseError = Exception

FLIGHT_TOOL: Tool = Tool(
    name="search_flights",
    description="Search for flight offers between two cities on given dates.",
    inputSchema={
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "IATA city/airport code (e.g. NYC)"},
            "destination": {"type": "string", "description": "IATA city/airport code (e.g. TYO)"},
            "departure_date": {"type": "string", "description": "Departure date in YYYY-MM-DD format"},
            "return_date": {"type": "string", "description": "Return date in YYYY-MM-DD format (optional)"},
            "adults": {"type": "integer", "description": "Number of adult passengers", "default": 1},
        },
        "required": ["origin", "destination", "departure_date"],
    },
)

HOTEL_TOOL: Tool = Tool(
    name="search_hotels",
    description="Search for hotel offers in a city.",
    inputSchema={
        "type": "object",
        "properties": {
            "city_code": {"type": "string", "description": "IATA city code (e.g. TYO)"},
            "check_in": {"type": "string", "description": "Check-in date in YYYY-MM-DD format"},
            "check_out": {"type": "string", "description": "Check-out date in YYYY-MM-DD format"},
            "adults": {"type": "integer", "description": "Number of adult guests", "default": 1},
        },
        "required": ["city_code", "check_in", "check_out"],
    },
)

BOOKING_TOOL: Tool = Tool(
    name="create_booking",
    description="Create a sandbox flight booking for a selected flight offer.",
    inputSchema={
        "type": "object",
        "properties": {
            "flight_offer": {
                "type": "object",
                "description": "The flight offer object from search_flights results",
            },
            "travelers": {
                "type": "array",
                "description": "List of traveler information objects",
                "items": {
                    "type": "object",
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "age": {"type": "integer"},
                    },
                },
            },
        },
        "required": ["flight_offer", "travelers"],
    },
)

MOCK_FLIGHTS: dict[str, list[dict[str, Any]]] = {
    "NYC-TYO": [
        {"airline": "Mock Airlines", "flight_number": "MA101", "departure": "07:00", "arrival": "10:30+1", "price": 850, "currency": "USD"},
        {"airline": "Mock Airlines", "flight_number": "MA202", "departure": "22:00", "arrival": "15:00+1", "price": 680, "currency": "USD"},
    ],
    "TYO-NYC": [
        {"airline": "Mock Airlines", "flight_number": "MA303", "departure": "09:00", "arrival": "08:30+1", "price": 920, "currency": "USD"},
        {"airline": "Mock Airlines", "flight_number": "MA404", "departure": "17:00", "arrival": "14:30+1", "price": 750, "currency": "USD"},
    ],
    "LON-TYO": [
        {"airline": "Mock Airways", "flight_number": "MW505", "departure": "11:00", "arrival": "07:00+1", "price": 720, "currency": "USD"},
    ],
    "TYO-LON": [
        {"airline": "Mock Airways", "flight_number": "MW606", "departure": "12:00", "arrival": "16:00", "price": 780, "currency": "USD"},
    ],
}

MOCK_HOTELS: dict[str, list[dict[str, Any]]] = {
    "TYO": [
        {"hotel_name": "Mock Grand Tokyo", "room_type": "Standard", "price_per_night": 180, "currency": "USD"},
        {"hotel_name": "Mock Capsule Inn", "room_type": "Single", "price_per_night": 65, "currency": "USD"},
    ],
    "LON": [
        {"hotel_name": "Mock London Suites", "room_type": "Double", "price_per_night": 210, "currency": "USD"},
    ],
    "NYC": [
        {"hotel_name": "Mock NYC Hotel", "room_type": "Standard", "price_per_night": 250, "currency": "USD"},
    ],
}

def _lookup_mock_flights(origin: str, destination: str) -> list[dict]:
    key = f"{origin.upper()}-{destination.upper()}"
    reverse_key = f"{destination.upper()}-{origin.upper()}"
    results = MOCK_FLIGHTS.get(key) or MOCK_FLIGHTS.get(reverse_key, [])
    if not results:
        results = [
            {"airline": "Mock Global Air", "flight_number": "MG001", "departure": "08:00", "arrival": "12:00", "price": 500, "currency": "USD"},
        ]
    return results

def _lookup_mock_hotels(city_code: str) -> list[dict]:
    return MOCK_HOTELS.get(city_code.upper(), [
        {"hotel_name": f"Mock {city_code} Hotel", "room_type": "Standard", "price_per_night": 120, "currency": "USD"},
    ])


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [FLIGHT_TOOL, HOTEL_TOOL, BOOKING_TOOL]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info("MCP tool called: %s with args: %s", name, arguments)
    if name == "search_flights":
        result = await _search_flights(arguments)
    elif name == "search_hotels":
        result = await _search_hotels(arguments)
    elif name == "create_booking":
        result = await _create_booking(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _search_flights(args: dict) -> dict:
    origin = args["origin"]
    destination = args["destination"]
    departure_date = args["departure_date"]
    adults = args.get("adults", 1)

    if _amadeus_client:
        try:
            params = {
                "originLocationCode": origin.upper(),
                "destinationLocationCode": destination.upper(),
                "departureDate": departure_date,
                "adults": str(adults),
            }
            if args.get("return_date"):
                params["returnDate"] = args["return_date"]
            resp = _amadeus_client.shopping.flight_offers_search.get(**params)
            offers = resp.data
            return {"status": "success", "source": "amadeus", "flights": offers}
        except ResponseError as e:
            logger.warning("Amadeus API error, falling back to mock data: %s", e)

    flights = _lookup_mock_flights(origin, destination)
    return {"status": "success", "source": "mock", "flights": flights}


async def _search_hotels(args: dict) -> dict:
    city_code = args["city_code"]
    check_in = args["check_in"]
    check_out = args["check_out"]
    adults = args.get("adults", 1)

    if _amadeus_client:
        try:
            resp = _amadeus_client.shopping.hotel_offers_search.get(
                cityCode=city_code.upper(),
                checkInDate=check_in,
                checkOutDate=check_out,
                adults=str(adults),
            )
            offers = resp.data
            return {"status": "success", "source": "amadeus", "hotels": offers}
        except ResponseError as e:
            logger.warning("Amadeus API error, falling back to mock data: %s", e)

    hotels = _lookup_mock_hotels(city_code)
    return {"status": "success", "source": "mock", "hotels": hotels}


async def _create_booking(args: dict) -> dict:
    flight_offer = args["flight_offer"]
    travelers = args["travelers"]

    if _amadeus_client:
        try:
            resp = _amadeus_client.booking.flight_orders.post(flight_offer, travelers)
            return {"status": "confirmed", "source": "amadeus", "booking": resp.data}
        except ResponseError as e:
            logger.warning("Amadeus booking error, falling back to mock: %s", e)

    return {
        "status": "confirmed",
        "source": "mock",
        "booking_reference": "MOCK-BKG-001",
        "flight": flight_offer,
        "travelers": travelers,
    }


async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
