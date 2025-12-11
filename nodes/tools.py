# nodes/tools.py
import os
import time
import openrouteservice
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from geopy.geocoders import Nominatim
# Ensure Models are imported correctly
from .models import ExtractedLocations, RankedAttractionsList, GuardrailOutcome

# --- Load API Keys ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

# --- 1. The Retry Wrapper (CRITICAL FOR FREE TIER) ---


class RetryRunnable:
    """Wraps any LangChain runnable to handle Gemini 429 errors manually."""

    def __init__(self, runnable):
        self.runnable = runnable

    def invoke(self, *args, **kwargs):
        retries = 0
        max_retries = 3

        while True:
            try:
                return self.runnable.invoke(*args, **kwargs)
            except Exception as e:
                error_str = str(e)
                # Check for Rate Limit (429) OR Service Unavailable (503)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str:
                    retries += 1
                    if retries > max_retries:
                        print(
                            f"   > ❌ Max retries ({max_retries}) exceeded. Giving up.")
                        raise e

                    # Smart Backoff: Wait 20s, then 35s, then 50s
                    wait_time = 20 + (retries * 15)
                    print(
                        f"   > ⚠️ Gemini Rate Limit hit. Cooling down for {wait_time}s... (Attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    # If it's a real error (like bad JSON), crash immediately
                    raise e

# --- 2. The LLM Wrapper ---


class RateLimitAwareLLM:
    def __init__(self, model_name, api_key):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0,
            request_timeout=60
        )

    @property
    def robust_llm(self):
        return RetryRunnable(self.llm)

    def with_structured_output(self, schema):
        base_runnable = self.llm.with_structured_output(schema)
        return RetryRunnable(base_runnable)


# --- 3. Initialize Tools ---
# USING YOUR PREFERRED MODEL
wrapper = RateLimitAwareLLM("gemini-2.5-flash-lite", GOOGLE_API_KEY)

llm = wrapper.robust_llm
structured_llm = wrapper.with_structured_output(ExtractedLocations)
ranking_llm = wrapper.with_structured_output(RankedAttractionsList)
guardrail_llm = wrapper.with_structured_output(GuardrailOutcome)

# --- Other Tools ---
# FIX: Unique user_agent is required by Nominatim terms of service
geolocator = Nominatim(user_agent="sri_lanka_travel_agent_pro_v1")
ors_client = openrouteservice.Client(key=ORS_API_KEY)
