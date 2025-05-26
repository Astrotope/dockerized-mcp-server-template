from typing import Union, Dict, Optional
from open_meteo import OpenMeteo

def degrees_to_compass(degrees):
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    idx = int((degrees + 11.25) % 360 / 22.5)
    return directions[idx]

async def get_weather_summary(
    lat: Optional[float],
    lon: Optional[float]
) -> Dict[str, Union[float, str, None]]:
    # Validate coordinates
    if lat is None or lon is None:
        return {
            "temperature": None,
            "wind_speed": None,
            "wind_direction": None,
            "status": "Missing or invalid coordinates"
        }

    try:
        async with OpenMeteo() as open_meteo:
            forecast = await open_meteo.forecast(
                latitude=lat,
                longitude=lon,
                current_weather=True,
            )
            cw = forecast.current_weather
            return {
                "temperature": cw.temperature,
                "wind_speed": cw.wind_speed,
                "wind_direction": degrees_to_compass(cw.wind_direction),
                "status": "success"
            }
    except Exception as e:
        return {
            "temperature": None,
            "wind_speed": None,
            "wind_direction": None,
            "status": f"Weather API error: {str(e)}"
        }