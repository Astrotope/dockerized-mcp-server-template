from typing import Optional, Dict
import requests
import urllib.parse

def get_coordinates(place_name: str) -> Dict[str, Optional[str]]:
    """
    Get latitude and longitude for a place name using the Maps.co geocoding API.

    Args:
        place_name (str): The name of the place to geocode.

    Returns:
        dict: {
            "latitude": Optional[str],
            "longitude": Optional[str],
            "status": str
        }
    """
    api_key = "68344918e32a5644793637ofbf618cd"
    base_url = "https://geocode.maps.co/search"
    
    encoded_place = urllib.parse.quote(place_name)
    url = f"{base_url}?q={encoded_place}&api_key={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            first_result = data[0]
            return {
                "latitude": first_result.get("lat"),
                "longitude": first_result.get("lon"),
                "status": "success"
            }
        
        return {
            "latitude": None,
            "longitude": None,
            "status": "no results found"
        }
    
    except requests.RequestException as e:
        return {
            "latitude": None,
            "longitude": None,
            "status": f"Request error: {e}"
        }
    
    except ValueError as e:
        return {
            "latitude": None,
            "longitude": None,
            "status": f"JSON decode error: {e}"
        }
