#!/usr/bin/env python3
"""
Test if there are multiple flight segments for DL562 on this date
"""
import os
from pyfr24 import FR24API

# Initialize API
token = os.environ.get("FLIGHTRADAR_API_KEY")
api = FR24API(token)

print("=== TESTING FLIGHT LOOKUP FOR MULTIPLE SEGMENTS ===")
print()

# Test: Look up DL562 for the date to see all flight instances
flight_number = "DL562"
date = "2025-08-02"

print(f"Looking up all {flight_number} flights on {date}...")
print()

try:
    # Use the same lookup our smart-export uses
    flight_datetime_from = f"{date}T00:00:00Z"
    flight_datetime_to = f"{date}T23:59:59Z"
    
    summary = api.get_flight_summary_full(
        flights=flight_number, 
        flight_datetime_from=flight_datetime_from, 
        flight_datetime_to=flight_datetime_to
    )
    
    data = summary.get('data', [])
    print(f"Found {len(data)} flight instances:")
    print()
    
    for i, flight in enumerate(data):
        flight_id = flight.get('fr24_id', 'N/A')
        origin = flight.get('orig_icao', 'N/A')
        dest = flight.get('dest_icao', 'N/A') 
        takeoff = flight.get('datetime_takeoff', 'N/A')
        landed = flight.get('datetime_landed', 'N/A')
        
        print(f"Flight {i+1}: {flight_id}")
        print(f"  Route: {origin} -> {dest}")
        print(f"  Takeoff: {takeoff}")
        print(f"  Landed: {landed}")
        print()
        
        # Test tracks for each flight ID
        print(f"  Testing tracks for {flight_id}...")
        try:
            tracks_data = api.get_flight_tracks(flight_id)
            if isinstance(tracks_data, list) and tracks_data:
                tracks = tracks_data[0].get("tracks", [])
            elif isinstance(tracks_data, dict):
                tracks = tracks_data.get("tracks", [])
            else:
                tracks = []
                
            if tracks:
                sorted_tracks = sorted(tracks, key=lambda x: x.get("timestamp", ""))
                print(f"    Tracks: {len(sorted_tracks)} points")
                print(f"    First: {sorted_tracks[0].get('timestamp')}")
                print(f"    Last: {sorted_tracks[-1].get('timestamp')}")
                
                # Check final position
                last_track = sorted_tracks[-1]
                if 'lat' in last_track and 'lon' in last_track:
                    final_lat, final_lon = float(last_track['lat']), float(last_track['lon'])
                    atlanta_lat, atlanta_lon = 33.64, -84.43
                    distance = ((final_lat - atlanta_lat)**2 + (final_lon - atlanta_lon)**2)**0.5
                    print(f"    Final pos: {final_lat:.2f}, {final_lon:.2f}")
                    print(f"    Distance to ATL: ~{distance * 69:.0f} miles")
                    print(f"    Final altitude: {last_track.get('alt', 'N/A')} ft")
            else:
                print(f"    No tracks available")
        except Exception as e:
            print(f"    Error getting tracks: {e}")
        print()
        
except Exception as e:
    print(f"Error looking up flights: {e}")

print("=== SUMMARY ===")
print("If we find multiple flight instances with different")
print("track coverage, we may need to combine them or")
print("choose the most complete one.")