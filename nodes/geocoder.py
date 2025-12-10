from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from .graph_state import GraphState
from .tools import geolocator


def geocode_locations_node(state: GraphState):
    """
    Node 2: Geocodes the origin and destination names.
    """
    print("--- 2. EXECUTING: geocode_locations_node ---")
    origin = state.get("origin_name")
    destination = state.get("destination_name")

    origin_coords = None
    destination_coords = None

    try:
        if origin:
            location = geolocator.geocode(origin)
            if location:
                origin_coords = (location.latitude, location.longitude)
                print(f"   > Geocoded Origin '{origin}': {origin_coords}")
            else:
                print(f"   > WARNING: Could not geocode origin: {origin}")

        if destination:
            location = geolocator.geocode(destination)
            if location:
                destination_coords = (location.latitude, location.longitude)
                print(
                    f"   > Geocoded Destination '{destination}': {destination_coords}")
            else:
                print(
                    f"   > WARNING: Could not geocode destination: {destination}")

    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"   > ERROR: Geocoding service error: {e}")

    return {
        "origin_coords": origin_coords,
        "destination_coords": destination_coords
    }
