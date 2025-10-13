#!/usr/bin/env python3
"""
Check if the "complete" flights actually reached their destinations
"""
import os
from pyfr24 import FR24API

# Initialize API
token = os.environ.get("FLIGHTRADAR_API_KEY")
api = FR24API(token)

print("=== CHECKING IF FLIGHTS REACHED DESTINATIONS ===")
print()

# Airport coordinates (approximate)
airports = {
    "KJFK": (40.64, -73.78),  # JFK New York
    "KSFO": (37.62, -122.38), # San Francisco
    "KBDL": (41.74, -72.65),  # Bradley Hartford
    "KLAX": (33.94, -118.41), # Los Angeles
    "KSEA": (47.45, -122.31), # Seattle
    "KATL": (33.64, -84.43),  # Atlanta
}

flights_to_check = [
    {
        "flight": "AS227", 
        "flight_id": "3b8b3362", 
        "origin": "KJFK", 
        "dest": "KSFO",
        "final_pos": (41.43, -115.47),
        "final_alt": 34000
    },
    {
        "flight": "SY8924", 
        "flight_id": "3b8b059e", 
        "origin": "KBDL", 
        "dest": "KLAX",
        "final_pos": (34.19, -117.07),
        "final_alt": 20650
    },
    {
        "flight": "DL562", 
        "flight_id": "3b8b02be", 
        "origin": "KSEA", 
        "dest": "KATL",
        "final_pos": (39.28, -94.72),
        "final_alt": 33000
    }
]

def distance_miles(pos1, pos2):
    """Calculate approximate distance in miles"""
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5 * 69

for flight_info in flights_to_check:
    flight = flight_info["flight"]
    origin = flight_info["origin"]
    dest = flight_info["dest"]
    final_pos = flight_info["final_pos"]
    final_alt = flight_info["final_alt"]
    
    origin_coords = airports[origin]
    dest_coords = airports[dest]
    
    # Calculate distances
    dist_to_origin = distance_miles(final_pos, origin_coords)
    dist_to_dest = distance_miles(final_pos, dest_coords)
    total_route_distance = distance_miles(origin_coords, dest_coords)
    
    # Calculate progress percentage
    progress = (total_route_distance - dist_to_dest) / total_route_distance * 100
    
    print(f"=== {flight} ({origin} -> {dest}) ===")
    print(f"Final position: {final_pos[0]:.2f}, {final_pos[1]:.2f}")
    print(f"Final altitude: {final_alt} ft")
    print(f"Distance to origin ({origin}): {dist_to_origin:.0f} miles")
    print(f"Distance to destination ({dest}): {dist_to_dest:.0f} miles")
    print(f"Total route distance: {total_route_distance:.0f} miles")
    print(f"Progress: {progress:.1f}%")
    
    # Determine if flight reached destination
    if dist_to_dest < 50 and final_alt < 5000:  # Within 50 miles and low altitude
        print("✅ REACHED DESTINATION")
    elif progress > 95 and final_alt < 15000:  # Very close and descending
        print("✅ LIKELY REACHED DESTINATION")
    elif final_alt > 25000:  # High altitude
        print("❌ INCOMPLETE - Still at cruise altitude")
    elif progress < 80:  # Less than 80% of route
        print("❌ INCOMPLETE - Far from destination")
    else:
        print("⚠️  UNCLEAR - Need more analysis")
    
    print()

print("🎯 CONCLUSION:")
print("If AS227 and SY8924 are also incomplete (still at cruise altitude")
print("far from destination), then ALL flights have incomplete tracking.")
print("If they reached their destinations, then DL562 has a specific issue.")