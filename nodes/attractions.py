# nodes/attractions.py
import requests
import traceback
import math
from .graph_state import GraphState
from .tools import GEOAPIFY_API_KEY

GEOAPIFY_URL = "https://api.geoapify.com/v2/places"


def fetch_places_for_point(lat, lon, limit=5):
    """
    Helper function to call Geoapify for a specific point.
    Uses the KNOWN WORKING query structure (V10).
    """

    # --- *** THIS IS THE KNOWN-GOOD QUERY *** ---
    # We are using the query structure that we PROVED works.
    querystring = {
        "categories": "tourism",  # Use the broad, single category that works
        "filter": f"circle:{lon},{lat},10000",  # 10km radius
        "bias": f"proximity:{lon},{lat}",      # Keep the bias param
        "limit": limit,
        "apiKey": GEOAPIFY_API_KEY
    }
    # --- *** END OF QUERY *** ---

    try:
        response = requests.get(GEOAPIFY_URL, params=querystring)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # We'll print the error but continue, so one bad call doesn't stop the whole thing
        print(f"   > API Error for point {lat},{lon}: {e}")
        return {}


def get_attractions_node(state: GraphState):
    """
    Node 4: Fetches attractions using "Route Percentile Sampling" (10% intervals).
    (Version 17: Correct API query + 10% Sampling)
    """
    print("--- 4. EXECUTING: get_attractions_node (10% ROUTE SAMPLING) ---")

    destination_coords = state.get("destination_coords")
    route_path = state.get("route_path_coords")  # List of [lon, lat]

    if not destination_coords:
        return {}
    if not route_path or len(route_path) < 10:
        print("   > ERROR: Route path is missing or too short. Defaulting to destination-only search.")
        # Fallback: just search the destination
        route_path = [[destination_coords[1], destination_coords[0]]]

    all_places_to_search = []

    # 1. Get the 10 sample points
    path_len = len(route_path)

    # Get 10%, 20%, ..., 90% marks
    for i in range(1, 10):  # Loops 1, 2, ... 9
        percent = i * 10
        idx = int(path_len * (percent / 100.0))

        # Ensure index is valid
        if idx >= path_len:
            idx = path_len - 1

        point = route_path[idx]
        lon, lat = point[0], point[1]
        all_places_to_search.append({
            "lat": lat,
            "lon": lon,
            "tag": f"Stopover (~{percent}% mark)"
        })

    # Add the final destination (100% mark)
    dest_lat, dest_lon = destination_coords
    all_places_to_search.append({
        "lat": dest_lat,
        "lon": dest_lon,
        "tag": "Destination (100% mark)"
    })

    # 2. Call the API for all 10 points and merge
    combined_places = []
    seen_names = set()

    def process_results(data, tag):
        if "features" in data and isinstance(data["features"], list):
            for place in data["features"]:
                props = place.get("properties", {})
                name = props.get("name")
                if name and name not in seen_names:
                    seen_names.add(name)
                    all_kinds = ", ".join(props.get("categories", ["N/A"]))
                    combined_places.append({
                        "name": name,
                        "kinds": all_kinds,
                        "location_context": tag
                    })

    # Loop through our 10 search points
    for search_point in all_places_to_search:
        print(f"   > Fetching places {search_point['tag']}...")
        # Get 5 places per stopover, 15 for the (more important) destination
        limit = 15 if "Destination" in search_point["tag"] else 5
        api_data = fetch_places_for_point(
            search_point["lat"], search_point["lon"], limit=limit)
        process_results(api_data, search_point['tag'])

    print(
        f"   > Found {len(combined_places)} total unique places to be ranked.")

    return {
        "attractions": combined_places
    }
