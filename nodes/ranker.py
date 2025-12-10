# nodes/ranker.py
import json
import traceback
from .graph_state import GraphState
from .tools import ranking_llm


def rank_attractions_node(state: GraphState):
    """
    Node 5: Ranks attractions based on query, duration, AND drive time.
    """
    print("--- 5. EXECUTING: rank_attractions_node (LLM Judge) ---")

    original_query = state.get("original_query")
    attractions = state.get("attractions")

    # Context Variables
    duration = state.get("trip_duration_days") or 1
    drive_time = state.get("route_duration_str") or "unknown"
    origin_name = state.get("origin_name")
    destination_name = state.get("destination_name")

    if not original_query or not attractions:
        print("   > ERROR: Missing query or attractions list. Skipping ranking.")
        return {}

    # Create the list for the LLM
    attraction_list_str = "\n".join(
        [f"- {a['name']} (Category: {a['kinds']}, Context: {a['location_context']})" for a in attractions]
    )

    # --- UPDATED PROMPT (TUNED FOR VOLUME) ---
    prompt = f"""
    You are an elite travel itinerary planner for Sri Lanka.
    Your goal is to curate a FULL, realistic itinerary. Do not leave the user with empty days.

    --------------------------
    TRIP CONTEXT:
    - User Request: "{original_query}"
    - Origin: {origin_name}
    - Destination: {destination_name}
    - Trip Duration: {duration} days
    - Total Driving Time: {drive_time}
    --------------------------

    RAW CANDIDATE LIST (from API):
    {attraction_list_str}

    --------------------------
    YOUR INSTRUCTIONS:

    1. **CALCULATE THE TARGET COUNT (Crucial):**
       - **1 Day / Rushed Trip:** Select **5-7** attractions. Focus on the absolute highlights and efficient routing.
       - **2-3 Days:** Select **10-15** attractions. The user has plenty of time. Fill their days with a mix of major landmarks and scenic stops.
       - **4+ Days:** Select **15-20** attractions. This is a deep-dive trip. Include hidden gems, viewpoints, and cultural sites.
       - **RULE:** Do NOT limit the list to 5 items unless it is a very short (half-day) trip. If the user has 3 days, they need more than 5 places to visit!

    2. **JOURNEY DISTRIBUTION:**
       - Prioritize "Stopover" locations (from the middle of the route) to break up the driving.
       - Then fill the rest with "Destination" locations.

    3. **NOISE FILTERING (Keep Standards High):**
       - IGNORE generic infrastructure (Banks, Supermarkets, Bus Stands).
       - KEEP all specific tourist spots: Viewpoints, Waterfalls, Temples, Statues, Historic Buildings, Parks.
       - If a hotel is famous/historic (e.g. Queens Hotel), keep it. If it's just "Guest House," ignore it.

    --------------------------
    OUTPUT REQUIREMENT:
    Return a JSON list of the selected top attractions (Aim for the target count calculated above).
    For each, the 'reasoning' must explain:
    1. Why it's good.
    2. How it fits the schedule (e.g. "Good for Day 1 stopover" or "Visit on Day 2 in Kandy").
    """
    # --- END PROMPT ---

    try:
        response = ranking_llm.invoke(prompt)

        ranked_list = [
            {"name": a.name, "reasoning": a.reasoning}
            for a in response.top_attractions
        ]

        print(
            f"   > Successfully ranked {len(ranked_list)} attractions for a {duration}-day trip.")

        return {
            "ranked_attractions": ranked_list
        }

    except Exception as e:
        print(f"   > ERROR: LLM ranking failed:")
        print(traceback.format_exc())
        return {}
