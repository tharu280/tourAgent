# nodes/tools.py
import os
import time
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

# --- 1. The Retry Wrapper (Crash Prevention) ---


class RetryRunnable:
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
                # Catch Rate Limits (429) and "Model Overloaded" (503)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str:
                    retries += 1
                    if retries > max_retries:
                        print(f"   > ❌ Max retries ({max_retries}) exceeded.")
                        raise e

                    wait_time = 20 + (retries * 15)
                    print(f"   > ⚠️ Rate Limit hit. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
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
# CORRECT MODEL NAME: gemini-1.5-flash
# (There is no 2.5 yet!)
wrapper = RateLimitAwareLLM("gemini-1.5-flash", GOOGLE_API_KEY)

llm = wrapper.robust_llm
structured_llm = wrapper.with_structured_output(ExtractedLocations)
ranking_llm = wrapper.with_structured_output(RankedAttractionsList)
guardrail_llm = wrapper.with_structured_output(GuardrailOutcome)

# --- Other Tools ---
geolocator = Nominatim(user_agent="sri_lanka_travel_agent_pro_v1")
ors_client = openrouteservice.Client(key=ORS_API_KEY)
