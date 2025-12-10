# run_workflow.py
import pprint
from langgraph.graph import StateGraph, END

from nodes.graph_state import GraphState
from nodes.guardrail import input_guardrail_node
from nodes.extractor import extract_locations_node
from nodes.geocoder import geocode_locations_node
from nodes.router import get_route_node
from nodes.attractions import get_attractions_node
from nodes.ranker import rank_attractions_node
from nodes.itinerary_builder import build_itinerary_node # <-- 1. Import

# --- Conditional Logic ---
def decide_next_step(state: GraphState):
    decision = state.get("guardrail_decision")
    if decision == "valid":
        return "extract_locations"
    else:
        return END

# --- Build Graph ---
workflow = StateGraph(GraphState)

workflow.add_node("guardrail", input_guardrail_node)
workflow.add_node("extract_locations", extract_locations_node)
workflow.add_node("geocode_locations", geocode_locations_node)
workflow.add_node("get_route", get_route_node)
workflow.add_node("get_attractions", get_attractions_node)
workflow.add_node("rank_attractions", rank_attractions_node)
workflow.add_node("build_itinerary", build_itinerary_node) # <-- 2. Add Node

workflow.set_entry_point("guardrail")

workflow.add_conditional_edges(
    "guardrail",
    decide_next_step,
    {
        "extract_locations": "extract_locations",
        END: END
    }
)

workflow.add_edge("extract_locations", "geocode_locations")
workflow.add_edge("geocode_locations", "get_route")
workflow.add_edge("get_route", "get_attractions")
workflow.add_edge("get_attractions", "rank_attractions")
workflow.add_edge("rank_attractions", "build_itinerary") # <-- 3. Connect to Itinerary
workflow.add_edge("build_itinerary", END)                # <-- 4. End here

app_graph = workflow.compile()

# --- Run ---
if __name__ == "__main__":
    print("--- Starting Trip Planner Workflow ---")

    test_query = input("Enter your travel query: ")
    if not test_query:
        test_query = "I wanna go from kandy to colombo, 2 days"

    inputs = {"original_query": test_query}

    final_state = app_graph.invoke(inputs)

    print("\n--- FINAL STATE (Cleaned) ---")
    
    # Clean up for display
    final_state.pop("route_geojson", None)
    final_state.pop("route_path_coords", None)
    final_state.pop("attractions", None)
    
    # Extract and print the itinerary separately for readability
    itinerary = final_state.pop("final_itinerary", "No itinerary generated.")
    
    # Print the data structure
    pprint.pprint(final_state)
    
    print("\n" + "="*50)
    print("📝 GENERATED ITINERARY:")
    print("="*50)
    print(itinerary)