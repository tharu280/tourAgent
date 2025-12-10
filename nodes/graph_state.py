# nodes/graph_state.py
from typing import TypedDict, Optional, Any, List

class GraphState(TypedDict):
    original_query: str
    guardrail_decision: Optional[str] = None
    final_response: Optional[str] = None
    
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
    trip_duration_days: Optional[int] = None
    
    origin_coords: Optional[tuple] = None
    destination_coords: Optional[tuple] = None

    route_distance_km: Optional[float] = None
    route_duration_str: Optional[str] = None
    route_geojson: Optional[dict] = None
    route_path_coords: Optional[List[List[float]]] = None 

    attractions: Optional[List[dict]] = None 
    ranked_attractions: Optional[List[dict]] = None 
    
 
    final_itinerary: Optional[str] = None
    