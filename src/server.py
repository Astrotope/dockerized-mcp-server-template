# server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import requests
import urllib.parse
import json
from typing import Dict, Optional

from weather import get_weather_summary
from location import get_coordinates

# Create an MCP server
mcp = FastMCP("StatelessServer", stateless_http=True)

# Add an addition tool
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

# Add a multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def geocode_place(place_name: str) -> Dict[str, Optional[str]]:
    """
    Get latitude and longitude coordinates for a given place name.
    
    Args:
        place_name: The name of the place to geocode (e.g., "florida", "New York")
    
    Returns:
        A dictionary with 'latitude', 'longitude', and 'status' keys
    """
    lat, lon = get_coordinates(place_name)
    
    if lat and lon:
        return {
            "latitude": lat,
            "longitude": lon,
            "status": "success"
        }
    else:
        return {
            "latitude": None,
            "longitude": None,
            "status": f"No coordinates found for '{place_name}'"
        }

@mcp.tool()
def get_current_weather(place_name: str) -> Dict[str, Optional[str]]:
    """
    Get current weather summary (temperature, wind speed, direction) for a place.

    Args:
        place_name: Name of location (e.g., "Tokyo", "Berlin")

    Returns:
        Dictionary with weather data and status
    """
    lat, lon = get_coordinates(place_name)
    if not lat or not lon:
        return {
            "temperature": None,
            "wind_speed": None,
            "wind_direction": None,
            "status": f"Could not geocode '{place_name}'"
        }

    try:
        result = asyncio.run(get_weather_summary(float(lat), float(lon)))
        result["status"] = "success"
        return result
    except Exception as e:
        return {
            "temperature": None,
            "wind_speed": None,
            "wind_direction": None,
            "status": f"Error fetching weather: {str(e)}"
        }

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")