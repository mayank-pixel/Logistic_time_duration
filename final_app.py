# final_app.py (Stable Version with State Management)

import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium
import googlemaps

# Load model
model = joblib.load("route_time_predictor.pkl")

# Google Maps API key
GOOGLE_API_KEY = "AIzaSyBsH9Dn-6QkSS_p2ROTt7eW9SpnvArPg0c"
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# Define city list and coordinates
cities = ["Bengaluru", "Delhi", "Ahmedabad", "Visakhapatnam", "Mumbai", "Hyderabad", "Chennai", "Kolkata", "Pune", "Jaipur"]

city_coords = {
    "Bengaluru": (12.9716, 77.5946),
    "Delhi": (28.6139, 77.2090),
    "Ahmedabad": (23.0225, 72.5714),
    "Visakhapatnam": (17.6868, 83.2185),
    "Mumbai": (19.0760, 72.8777),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567),
    "Jaipur": (26.9124, 75.7873)
}

# Mock fuel prices per city
fuel_prices = {
    "Bengaluru": 97.0,
    "Delhi": 96.2,
    "Ahmedabad": 96.8,
    "Visakhapatnam": 99.0,
    "Mumbai": 106.3,
    "Hyderabad": 108.1,
    "Chennai": 102.4,
    "Kolkata": 106.5,
    "Pune": 105.0,
    "Jaipur": 109.2
}

vehicle_types = {
    "Mini Truck (10 km/l)": 10,
    "Medium Truck (6 km/l)": 6,
    "Heavy Truck (4 km/l)": 4
}

# Cache API call for distance
@st.cache_data(show_spinner=False)
def get_distance_km(origin, destination):
    result = gmaps.distance_matrix(origins=origin, destinations=destination, mode="driving")
    distance_m = result["rows"][0]["elements"][0]["distance"]["value"]
    return round(distance_m / 1000, 2)

# UI starts here
st.title("🚛 Smart Logistics Route Time & Cost Estimator")

vehicle_choice = st.selectbox("Select Vehicle Type", list(vehicle_types.keys()))
km_per_litre = vehicle_types[vehicle_choice]

multi_stop = st.selectbox("Do you want Multi-Stop Route?", ["No", "Yes"])

if multi_stop == "No":
    from_city = st.selectbox("From City", cities, key="from1")
    to_city = st.selectbox("To City", cities, key="to1")
    stops = [from_city, to_city]
else:
    stops = st.multiselect("Select Cities in Route Order", cities, default=["Bengaluru", "Hyderabad", "Kolkata"])

# Predict and store route
if st.button("Predict Route") and len(stops) >= 2:
    route_details = []
    total_distance = 0
    total_time = 0
    total_cost = 0

    for i in range(len(stops) - 1):
        origin = stops[i]
        dest = stops[i + 1]
        try:
            distance = get_distance_km(origin, dest)
            row = pd.DataFrame([[origin, dest, distance]], columns=["From", "To", "Distance (KM)"])
            time_pred = model.predict(row)[0]
            fuel_rate = fuel_prices.get(origin, 100.0)
            litres_used = distance / km_per_litre
            fuel_cost = round(fuel_rate * litres_used, 2)

            route_details.append((origin, dest, distance, time_pred, fuel_cost))
            total_distance += distance
            total_time += time_pred
            total_cost += fuel_cost

        except Exception as e:
            st.error(f"Error fetching {origin} to {dest}: {e}")

    # Save to session_state
    st.session_state.route_ready = True
    st.session_state.route_details = route_details
    st.session_state.total_distance = total_distance
    st.session_state.total_time = total_time
    st.session_state.total_cost = total_cost
    st.session_state.stops = stops

# Show results if prediction exists
if st.session_state.get("route_ready", False):
    st.subheader("📊 Route Summary")
    for origin, dest, dist, t, cost in st.session_state.route_details:
        st.write(f"**{origin} → {dest}**: {dist} km | {t:.2f} hrs | ₹{cost:.2f} fuel")

    st.success(f"Total Distance: **{st.session_state.total_distance:.2f} km**")
    st.success(f"Estimated Time: **{st.session_state.total_time:.2f} hrs**")
    st.success(f"Estimated Fuel Cost: ₹**{st.session_state.total_cost:.2f}**")

    # Map rendering
    stops = st.session_state.stops
    m = folium.Map(location=city_coords[stops[0]], zoom_start=5)
    for city in stops:
        if city in city_coords:
            folium.Marker(city_coords[city], tooltip=city).add_to(m)

    for i in range(len(stops) - 1):
        loc1 = city_coords.get(stops[i])
        loc2 = city_coords.get(stops[i + 1])
        if loc1 and loc2:
            folium.PolyLine([loc1, loc2], color="blue", weight=4).add_to(m)

    st_folium(m, width=700, height=500)
