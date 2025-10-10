"""MCP server for Boston Harbor ferry tracking."""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

from .client import APRSClient
from .vessels import VESSELS, LOCATIONS


# Initialize MCP server
app = Server("boston-harbor-ferries")


# Define available tools
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available ferry tracking tools."""
    return [
        Tool(
            name="track_ferry",
            description="Get current position and status of a Boston Harbor ferry by MMSI number",
            inputSchema={
                "type": "object",
                "properties": {
                    "mmsi": {
                        "type": "string",
                        "description": "Vessel MMSI number (e.g., '368157410' for Crispus Attucks)",
                    },
                    "use_cache": {
                        "type": "boolean",
                        "description": "Use cached data if available (default: true)",
                        "default": True,
                    },
                },
                "required": ["mmsi"],
            },
        ),
        Tool(
            name="track_all_ferries",
            description="Get current positions of all Boston Harbor commuter ferries",
            inputSchema={
                "type": "object",
                "properties": {
                    "use_cache": {
                        "type": "boolean",
                        "description": "Use cached data if available (default: true)",
                        "default": True,
                    },
                },
            },
        ),
        Tool(
            name="list_ferries",
            description="List all known Boston Harbor commuter ferries with their details",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_ferry_routes",
            description="Get information about ferry routes and schedules",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="clear_cache",
            description="Clear all cached ferry position data",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""

    if name == "list_ferries":
        ferries_info = []
        for mmsi, vessel in VESSELS.items():
            ferries_info.append({
                "mmsi": mmsi,
                "name": vessel.name,
                "route": vessel.route,
                "operator": vessel.operator,
                "capacity": vessel.capacity,
                "description": vessel.description,
            })

        return [
            TextContent(
                type="text",
                text=json.dumps(ferries_info, indent=2),
            )
        ]

    elif name == "get_ferry_routes":
        routes_info = {
            "North Station Route": {
                "stops": ["LoveJoy Wharf (North Station)", "Fan Pier (Seaport)", "Pier 10"],
                "travel_time_minutes": 30,
                "vessels": ["PHILLIS WHEATLEY", "SAMUEL WHITTEMORE", "COMMONWEALTH"],
            },
            "East Boston Route": {
                "stops": ["Lewis Mall Wharf (East Boston)", "Fan Pier (Seaport)"],
                "travel_time_minutes": 10,
                "vessels": ["CRISPUS ATTUCKS"],
            },
        }

        return [
            TextContent(
                type="text",
                text=json.dumps(routes_info, indent=2),
            )
        ]

    elif name == "track_ferry":
        mmsi = arguments.get("mmsi")
        use_cache = arguments.get("use_cache", True)

        with APRSClient() as client:
            position = client.get_vessel_position(mmsi, use_cache=use_cache)

            if position is None:
                return [
                    TextContent(
                        type="text",
                        text=f"No position data found for ferry {mmsi}",
                    )
                ]

            result = {
                "vessel": {
                    "name": position.vessel.name,
                    "mmsi": position.mmsi,
                    "route": position.vessel.route,
                },
                "position": {
                    "latitude": position.latitude,
                    "longitude": position.longitude,
                    "speed_knots": position.speed_knots,
                    "course_degrees": position.course_degrees,
                },
                "timestamp": position.timestamp.isoformat(),
                "age_seconds": position.age_seconds,
                "comment": position.comment,
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2),
                )
            ]

    elif name == "track_all_ferries":
        use_cache = arguments.get("use_cache", True)

        with APRSClient() as client:
            positions = client.get_all_ferries(use_cache=use_cache)

            results = []
            for pos in positions:
                results.append({
                    "vessel": {
                        "name": pos.vessel.name,
                        "mmsi": pos.mmsi,
                        "route": pos.vessel.route,
                    },
                    "position": {
                        "latitude": pos.latitude,
                        "longitude": pos.longitude,
                        "speed_knots": pos.speed_knots,
                        "course_degrees": pos.course_degrees,
                    },
                    "timestamp": pos.timestamp.isoformat(),
                    "age_seconds": pos.age_seconds,
                })

            return [
                TextContent(
                    type="text",
                    text=json.dumps(results, indent=2),
                )
            ]

    elif name == "clear_cache":
        with APRSClient() as client:
            client.clear_cache()

        return [
            TextContent(
                type="text",
                text="Cache cleared successfully",
            )
        ]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
