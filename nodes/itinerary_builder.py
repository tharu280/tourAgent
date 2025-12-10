# nodes/itinerary_builder.py
from langchain_core.messages import HumanMessage
from .graph_state import GraphState
from .tools import llm  # Import the raw LLM object

def build_itinerary_node(state: GraphState):
    """
    Node 6: Generates a day-by-day itinerary using the ranked attractions.
    """
    print("--- 6. EXECUTING: build_itinerary_node (STORYTELLER) ---")
    
    # 1. Gather Context
    origin = state.get("origin_name")
    destination = state.get("destination_name")
    days = state.get("trip_duration_days") or 1
    drive_time = state.get("route_duration_str")
    attractions = state.get("ranked_attractions", [])

    # 2. Format the attractions list for the prompt
    attractions_text = ""
    for i, place in enumerate(attractions, 1):
        attractions_text += f"{i}. {place['name']} ({place['reasoning']})\n"

    # 3. Construct the Prompt
    prompt = f"""
    You are an expert travel agent creating a personalized itinerary for Sri Lanka.
    
    TRIP DETAILS:
    - Route: {origin} to {destination}
    - Duration: {days} Days
    - Total Driving Time: {drive_time} (Approximate one-way drive)
    
    SELECTED ATTRACTIONS:
    {attractions_text}
    
    INSTRUCTIONS:
    Create a logical, day-by-day itinerary in Markdown format.
    
    1. **Pacing:** - Day 1 should include the travel from {origin} to {destination}.
       - Schedule "stopover" attractions (if any) during the drive on Day 1.
       - Schedule the main destination attractions for Day 2 onwards (or the afternoon of Day 1 if it's a short trip).
       
    2. **Structure:**
       - Use headings like "## Day 1: The Journey Begins".
       - Use bullet points for Morning / Afternoon / Evening activities.
       - Explicitly mention *when* to visit the selected attractions.
       
    3. **Tone:**
       - Be inviting, professional, and helpful.
       - Add small tips (e.g., "Best visited in the morning", "Don't forget your camera").
       
    4. **Gap Filling:**
       - If the list of attractions is short, you can suggest generic activities (e.g., "Enjoy a local lunch", "Relax at the hotel") to fill the gaps, but focus primarily on the provided list.
    """

    try:
        # Call the LLM directly
        response = llm.invoke([HumanMessage(content=prompt)])
        itinerary_text = response.content
        
        print("   > Itinerary generated successfully.")
        
        return {
            "final_itinerary": itinerary_text
        }

    except Exception as e:
        print(f"   > ERROR: Itinerary generation failed: {e}")
        return {"final_itinerary": "Sorry, I couldn't generate the detailed itinerary text."}