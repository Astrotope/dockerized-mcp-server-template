# server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import requests
import urllib.parse
import json
from typing import Dict, Optional

def get_coordinates(place_name):
    """
    Get latitude and longitude for a place name.
    
    Args:
        place_name (str): The name of the place to geocode
        
    Returns:
        tuple: (latitude, longitude) as strings, or (None, None) if no results
    """
    api_key = "68344918e32a5644793637ofbf618cd"
    base_url = "https://geocode.maps.co/search"
    
    # URL encode the place name
    encoded_place = urllib.parse.quote(place_name)
    
    # Build the full URL
    url = f"{base_url}?q={encoded_place}&api_key={api_key}"
    
    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Return coordinates from first result if available
        if data and len(data) > 0:
            first_result = data[0]
            return first_result.get('lat'), first_result.get('lon')
        else:
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None, None

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