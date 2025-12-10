# nodes/router.py
import openrouteservice
import traceback
from .graph_state import GraphState
from .tools import ors_client


def _format_duration(seconds: int) -> str:
    """Helper function to convert seconds to 'Xh Ym' format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"


def get_route_node(state: GraphState):
    """
    Node 3: Fetches the route AND saves the path coordinates.
    """
    print("--- 3. EXECUTING: get_route_node ---")
    origin = state.get("origin_coords")
    destination = state.get("destination_coords")

    if not origin or not destination:
        print("   > ERROR: Missing coordinates. Skipping routing.")
        return {}

    try:
        # Nominatim (lat, lon) -> ORS (lon, lat)
        coords = [
            (origin[1], origin[0]),
            (destination[1], destination[0])
        ]

        route_request = {
            'coordinates': coords,
            'profile': 'driving-car',
            'preference': 'recommended',
            'format': 'geojson'
        }

        print("   > Sending request to OpenRouteService...")
        route_response = ors_client.directions(**route_request)

        feature = route_response['features'][0]
        summary = feature['properties']['summary']
        geometry = feature['geometry']

        # --- THIS IS THE CHANGE ---
        # Extract the full list of path coordinates [[lon, lat], ...]
        path_coords = geometry['coordinates']
        # --- END OF CHANGE ---

        distance_meters = summary['distance']
        duration_seconds = int(summary['duration'])

        distance_km = round(distance_meters / 1000, 1)
        duration_str = _format_duration(duration_seconds)

        print(f"   > Route found: {distance_km} km, {duration_str}")

        return {
            "route_distance_km": distance_km,
            "route_duration_str": duration_str,
            "route_geojson": geometry,
            "route_path_coords": path_coords  # <-- Save the path to the state
        }

    except openrouteservice.exceptions.ApiError as e:
        print(f"   > ERROR: ORS API returned an error: {e}")
    except Exception as e:
        print(f"   > ERROR: A completely unexpected error occurred.")
        print(traceback.format_exc())

    return {}
