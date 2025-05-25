import googlemaps
import pandas as pd
import time

# Initialize Google Maps client
gmaps = googlemaps.Client(key='AIzaSyBsH9Dn-6QkSS_p2ROTt7eW9SpnvArPg0c')  # Replace with your actual API key

# List of major Indian cities
cities = [
    "Bengaluru", "Delhi", "Ahmedabad", "Visakhapatnam",
    "Kolkata", "Mumbai", "Hyderabad", "Chennai", "Pune", "Jaipur"
]

# Create a dataset for all city-to-city combinations
data = []

for origin in cities:
    for destination in cities:
        if origin != destination:
            try:
                result = gmaps.distance_matrix(origins=origin, destinations=destination, mode="driving")
                element = result["rows"][0]["elements"][0]
                
                distance_km = element["distance"]["value"] / 1000  # meters to km
                duration_hr = element["duration"]["value"] / 3600  # seconds to hours
                fuel_cost = round(distance_km * 8, 2)  # ₹8 per km
                
                data.append([origin, destination, round(distance_km, 2), round(duration_hr, 2), fuel_cost])
                
                time.sleep(1)  # respect rate limit
            except Exception as e:
                print(f"Error processing {origin} → {destination}: {e}")

# Create DataFrame
df = pd.DataFrame(data, columns=["From", "To", "Distance (KM)", "Time (Hours)", "Fuel Cost (₹)"])

# Save as CSV
df.to_csv("real_india_city_routes.csv", index=False)
print("Saved as real_india_city_routes.csv")
