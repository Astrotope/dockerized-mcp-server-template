import argparse
import asyncio
from weather import get_weather_summary

def parse_args():
    parser = argparse.ArgumentParser(description="Get current weather from Open-Meteo.")
    parser.add_argument("--lat", type=float, required=True, help="Latitude (e.g. 52.52)")
    parser.add_argument("--lon", type=float, required=True, help="Longitude (e.g. 13.405)")
    return parser.parse_args()

def main():
    args = parse_args()
    result = asyncio.run(get_weather_summary(args.lat, args.lon))
    print("\nWeather Summary:")
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
