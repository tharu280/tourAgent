# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
import uvicorn

# Import our graph components
from nodes.graph_state import GraphState
from nodes.guardrail import input_guardrail_node
from nodes.extractor import extract_locations_node
from nodes.geocoder import geocode_locations_node
from nodes.router import get_route_node
from nodes.attractions import get_attractions_node
from nodes.ranker import rank_attractions_node
from nodes.itinerary_builder import build_itinerary_node  # <-- Added this import

# --- 1. Initialize FastAPI ---
app = FastAPI(
    title="AI Trip Planner API",
    description="Backend API for the Sri Lanka Travel Agent",
    version="1.0.0"
)

# --- 2. Define Request Model ---


class TripRequest(BaseModel):
    query: str

# --- 3. Build the LangGraph Workflow ---


def decide_next_step(state: GraphState):
    decision = state.get("guardrail_decision")
    if decision == "valid":
        return "extract_locations"
    else:
        return END


workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("guardrail", input_guardrail_node)
workflow.add_node("extract_locations", extract_locations_node)
workflow.add_node("geocode_locations", geocode_locations_node)
workflow.add_node("get_route", get_route_node)
workflow.add_node("get_attractions", get_attractions_node)
workflow.add_node("rank_attractions", rank_attractions_node)
workflow.add_node("build_itinerary", build_itinerary_node)  # <-- Added Node

# Define Flow
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
# <-- Connect Ranker to Builder
workflow.add_edge("rank_attractions", "build_itinerary")
# <-- End after Builder
workflow.add_edge("build_itinerary", END)

# Compile the graph
app_graph = workflow.compile()

# --- 4. Define the API Endpoint ---


@app.post("/plan-trip")
async def plan_trip(request: TripRequest):
    """
    Main endpoint: Receives query, orchestrates AI agents, returns itinerary.
    """
    print(f"📨 Request received: {request.query}")
    inputs = {"original_query": request.query}

    try:
        final_state = app_graph.invoke(inputs)

        # Clean up heavy data to reduce payload size for the frontend
        keys_to_remove = ["route_geojson", "route_path_coords", "attractions"]
        for key in keys_to_remove:
            if key in final_state:
                del final_state[key]

        return final_state

    except Exception as e:
        print(f"❌ Critical Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
