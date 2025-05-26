import requests
import urllib.parse
import json
import sys

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

if __name__ == "__main__":
    # Check if place name was provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: python geocode.py <place_name>")
        print("Example: python geocode.py florida")
        sys.exit(1)
    
    # Get place name from command line (join all arguments in case of spaces)
    place_name = " ".join(sys.argv[1:])
    
    lat, lon = get_coordinates(place_name)
    if lat and lon:
        print(f"Coordinates for '{place_name}': {lat}, {lon}")
    else:
        print(f"No coordinates found for '{place_name}'")