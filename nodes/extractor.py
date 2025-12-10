# nodes/extractor.py
from .graph_state import GraphState
from .tools import structured_llm


def extract_locations_node(state: GraphState):
    """
    Node 1: Extracts origin, destination, AND duration from the user query.
    """
    print("--- 1. EXECUTING: extract_locations_node ---")
    query = state["original_query"]

    prompt = f"""
    You are an expert at parsing travel queries.
    Extract the origin city, destination city, and trip duration (in days) from the following query:
    
    Query: "{query}"
    
    If no duration is mentioned, return null for days.
    """

    try:
        response = structured_llm.invoke(prompt)
        print(
            f"   > LLM Extracted: {response.origin} -> {response.destination} ({response.duration_days} days)")

        return {
            "origin_name": response.origin,
            "destination_name": response.destination,
            "trip_duration_days": response.duration_days  # Save to state
        }
    except Exception as e:
        print(f"   > ERROR in LLM extraction: {e}")
        return {
            "origin_name": None,
            "destination_name": None,
            "trip_duration_days": None
        }
