# nodes/tools.py
import os
import openrouteservice
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from geopy.geocoders import Nominatim
# Ensure GuardrailOutcome is imported here
from .models import ExtractedLocations, RankedAttractionsList, GuardrailOutcome

# --- Load API Keys ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found...")
if not ORS_API_KEY:
    raise ValueError("ORS_API_KEY not found...")
if not GEOAPIFY_API_KEY:
    raise ValueError(
        "GEOAPIFY_API_KEY not found. Please set it in your .env file.")

# --- Initialize Base LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    temperature=0
)

# --- Structured LLMs ---
# Node 1: Extractor
structured_llm = llm.with_structured_output(ExtractedLocations)

# Node 5: Ranker
ranking_llm = llm.with_structured_output(RankedAttractionsList)

# Node 0: Guardrail (THIS WAS MISSING)
guardrail_llm = llm.with_structured_output(GuardrailOutcome)

# --- Other Tools ---
geolocator = Nominatim(user_agent="ai_trip_planner_v1")
ors_client = openrouteservice.Client(key=ORS_API_KEY)
