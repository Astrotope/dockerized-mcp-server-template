# python src/location_test.py --place="San Francisco"

import argparse
from location import get_coordinates

def parse_args():
    parser = argparse.ArgumentParser(description="Get coordinates (latitude and longitude) for a place name.")
    parser.add_argument("--place", type=str, required=True, help="Place name to geocode (e.g. 'New York')")
    return parser.parse_args()

def main():
    args = parse_args()
    result = get_coordinates(args.place)
    
    print("\nCoordinates Result:")
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()