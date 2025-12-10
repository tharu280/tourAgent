# nodes/tools.py
import os
import time
import random
import openrouteservice
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from geopy.geocoders import Nominatim
from .models import ExtractedLocations, RankedAttractionsList, GuardrailOutcome

# --- Load API Keys ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

# --- Robust LLM Wrapper ---
# We wrap the LLM initialization to add automatic retries for Error 429


class RateLimitAwareLLM:
    def __init__(self, model_name, api_key):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0,
            max_retries=5,  # Built-in LangChain retry
            request_timeout=60
        )

    def with_structured_output(self, schema):
        return self.llm.with_structured_output(schema)

    def invoke(self, *args, **kwargs):
        return self.llm.invoke(*args, **kwargs)


# Initialize the robust LLM
_llm_wrapper = RateLimitAwareLLM("gemini-2.5-flash-lite", GOOGLE_API_KEY)

# Use this wrapper for everything
llm = _llm_wrapper.llm
structured_llm = llm.with_structured_output(ExtractedLocations)
ranking_llm = llm.with_structured_output(RankedAttractionsList)
guardrail_llm = llm.with_structured_output(GuardrailOutcome)

# --- Other Tools ---
# FIX: Use a unique user_agent to avoid blocking
geolocator = Nominatim(user_agent="sri_lanka_trip_planner_api_v1")
ors_client = openrouteservice.Client(key=ORS_API_KEY)
