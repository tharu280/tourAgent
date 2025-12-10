# app.py
import streamlit as st
import requests
import pandas as pd

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/plan-trip"

st.set_page_config(page_title="Sri Lanka AI Travel Agent",
                   page_icon="🇱🇰", layout="centered")

# --- Custom CSS for Chat Cards (Dark Text Force) ---
st.markdown("""
<style>
    .attraction-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #4F8BF9;
        margin-bottom: 10px;
        color: #31333F; /* Dark text for readability */
    }
    .attraction-name { 
        font-weight: bold; font-size: 1.1em; margin-bottom: 5px; color: #31333F; 
    }
    .attraction-reason { 
        font-size: 0.9em; color: #555; font-style: italic; 
    }
    .stat-row {
        display: flex; justify-content: space-between;
        background: #eef2f6; padding: 10px; border-radius: 8px;
        margin-bottom: 15px; font-size: 0.9rem; color: #31333F;
    }
    .stat-row span { color: #31333F !important; }
</style>
""", unsafe_allow_html=True)

st.title("🇱🇰 Sri Lanka AI Travel Agent")
st.caption("Powered by LangGraph, Gemini 2.5, and Geoapify")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ayubowan! 🙏 I can plan your perfect trip in Sri Lanka. \n\nTry saying: **'Plan a 3 day scenic trip from Colombo to Kandy'**"}]

# --- Display History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "itinerary_data" in message:
            data = message["itinerary_data"]

            # 1. Stats
            st.markdown(f"""
            <div class="stat-row">
                <span>🚗 <b>{data.get('route_distance_km')} km</b></span>
                <span>⏳ <b>{data.get('route_duration_str')}</b> drive</span>
                <span>📅 <b>{data.get('trip_duration_days')}</b> days</span>
            </div>
            """, unsafe_allow_html=True)

            # 2. Map
            o_coords = data.get("origin_coords")
            d_coords = data.get("destination_coords")
            if o_coords and d_coords:
                map_df = pd.DataFrame([
                    {"lat": o_coords[0], "lon": o_coords[1],
                        "color": "#FF0000"},
                    {"lat": d_coords[0], "lon": d_coords[1],
                        "color": "#00FF00"}
                ])
                st.map(map_df, latitude="lat",
                       longitude="lon", size=20, zoom=8)

            # 3. The Written Itinerary
            if data.get("final_itinerary"):
                st.markdown(data["final_itinerary"])

            # 4. Attraction Cards
            if data.get("ranked_attractions"):
                with st.expander("See Attraction Details"):
                    for i, place in enumerate(data["ranked_attractions"], 1):
                        st.markdown(f"""
                        <div class="attraction-card">
                            <div class="attraction-name">{i}. {place['name']}</div>
                            <div class="attraction-reason">{place['reasoning']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

# --- Handle Input ---
if prompt := st.chat_input("Where do you want to go?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 AI Agent is planning your journey..."):
            try:
                response = requests.post(API_URL, json={"query": prompt})
                if response.status_code == 200:
                    data = response.json()
                    if data.get("guardrail_decision") != "valid":
                        # Guardrail Rejection
                        response_text = data.get("final_response")
                        st.markdown(response_text)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response_text})
                    else:
                        # Valid Trip
                        st.session_state.messages.append(
                            {"role": "assistant", "content": "", "itinerary_data": data})
                        st.rerun()
                else:
                    st.error(f"Backend Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
