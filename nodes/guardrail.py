# nodes/guardrail.py
from .graph_state import GraphState
from .tools import guardrail_llm

def input_guardrail_node(state: GraphState):
    """
    Node 0: INTENT CLASSIFIER & SECURITY GATEWAY
    """
    print("--- 0. EXECUTING: input_guardrail_node (POLISHED MODE) ---")
    query = state["original_query"]
    
    prompt = f"""
    You are the intelligent, polite, and helpful Gatekeeper for a Travel Agent AI.
    Your job is to classify the user's input and provide a natural, polished response.

    USER INPUT: "{query}"

    -----------------------------------------
    YOUR CLASSIFICATION RULES:

    1. **"greeting"**: Simple hellos (e.g., "Hi", "Good morning").
    2. **"unrelated"**: Topics clearly outside travel planning (e.g., coding, politics, gibberish).
    3. **"incomplete"**: Travel queries missing specific details (Origin, Destination, or Duration).
    4. **"valid"**: Queries that clearly have Origin, Destination, AND Duration.

    -----------------------------------------
    INSTRUCTIONS FOR "feedback_message" (TONE: Professional, Warm, Natural):

    - **DO NOT** use labels like "Missing:" or strict templates. 
    - **DO NOT** use excessive markdown like bolding every other word. 
    - Write as if you are a helpful human concierge sending a text message.

    **Specific Scenarios:**

    - If **"greeting"**: 
      Warmly welcome them. Briefly mention you are ready to plan their trip and ask for their travel details.

    - If **"unrelated"**: 
      Politely apologize and explain that your expertise is strictly in planning travel itineraries. Gently guide them back to travel topics.

    - If **"incomplete"**: 
      In a natural sentence, identify what information you are missing (e.g., "I'd love to plan that for you, but I need to know how many days you have available."). 
      Then, gently suggest how they could phrase it (e.g., "Could you try again adding the duration? For example: 'Plan a 3-day trip from X to Y'.").

    - If **"valid"**: 
      Acknowledge the request enthusiastically (e.g., "That sounds like a fantastic trip! Let me crunch the numbers and find the best spots for you...").

    -----------------------------------------
    OUTPUT:
    Return the JSON with the 'decision' and your polished 'feedback_message'.
    """
    
    try:
        result = guardrail_llm.invoke(prompt)
        print(f"   > Decision: {result.decision.upper()}")
        
        return {
            "guardrail_decision": result.decision,
            "final_response": result.feedback_message
        }
    except Exception as e:
        print(f"   > Guardrail Error: {e}")
        return {
            "guardrail_decision": "error", 
            "final_response": "I'm having a little trouble understanding that. Could you try asking for a specific trip plan?"
        }