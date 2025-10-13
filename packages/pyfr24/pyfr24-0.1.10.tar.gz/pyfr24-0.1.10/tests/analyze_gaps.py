#!/usr/bin/env python3
"""
Analyze the flight track data for gaps and completeness
"""
import os
from datetime import datetime
from pyfr24 import FR24API

# Initialize API
token = os.environ.get("FLIGHTRADAR_API_KEY")
api = FR24API(token)

flight_id = "3b8b02be"  # Our DL562 flight

print("Analyzing flight track completeness...")
print(f"Flight ID: {flight_id}")
print()

# Get flight tracks
data = api.get_flight_tracks(flight_id)
if isinstance(data, dict) and "tracks" in data:
    tracks = data["tracks"]
elif isinstance(data, list):
    tracks = data[0]["tracks"] if data else []
else:
    tracks = []

if not tracks:
    print("No track data found")
    exit(1)

# Sort by timestamp
sorted_tracks = sorted(tracks, key=lambda x: x.get("timestamp", ""))

print(f"Total track points: {len(sorted_tracks)}")
print()

# Analyze timeline
first_time = datetime.fromisoformat(sorted_tracks[0]["timestamp"].replace('Z', '+00:00'))
last_time = datetime.fromisoformat(sorted_tracks[-1]["timestamp"].replace('Z', '+00:00'))
duration = last_time - first_time

print(f"Track timeline:")
print(f"  First point: {sorted_tracks[0]['timestamp']} (lat: {sorted_tracks[0]['lat']}, lon: {sorted_tracks[0]['lon']})")
print(f"  Last point:  {sorted_tracks[-1]['timestamp']} (lat: {sorted_tracks[-1]['lat']}, lon: {sorted_tracks[-1]['lon']})")
print(f"  Duration:    {duration}")
print()

# Expected flight info from toplines
print("Expected flight info:")
print(f"  Origin: KSEA (Seattle)")
print(f"  Destination: KATL (Atlanta ~33.64, -84.43)")
print(f"  Scheduled arrival: 2025-08-02T19:12:01Z (3:12 PM ET)")
print()

# Check if we reach Atlanta area
atlanta_lat, atlanta_lon = 33.64, -84.43
last_lat, last_lon = float(sorted_tracks[-1]['lat']), float(sorted_tracks[-1]['lon'])

# Calculate rough distance to Atlanta (degrees)
lat_diff = abs(last_lat - atlanta_lat)
lon_diff = abs(last_lon - atlanta_lon)
distance_deg = (lat_diff**2 + lon_diff**2)**0.5

print(f"Distance analysis:")
print(f"  Last position: {last_lat:.2f}, {last_lon:.2f}")
print(f"  Atlanta (KATL): {atlanta_lat:.2f}, {atlanta_lon:.2f}")
print(f"  Distance: ~{distance_deg:.1f} degrees (~{distance_deg * 69:.0f} miles)")
print()

# Look for gaps in data
print("Checking for time gaps...")
gap_threshold = 300  # 5 minutes in seconds

gaps = []
for i in range(1, len(sorted_tracks)):
    prev_time = datetime.fromisoformat(sorted_tracks[i-1]["timestamp"].replace('Z', '+00:00'))
    curr_time = datetime.fromisoformat(sorted_tracks[i]["timestamp"].replace('Z', '+00:00'))
    gap = (curr_time - prev_time).total_seconds()
    
    if gap > gap_threshold:
        gaps.append({
            'start': sorted_tracks[i-1]["timestamp"],
            'end': sorted_tracks[i]["timestamp"],
            'duration': gap / 60  # in minutes
        })

if gaps:
    print(f"Found {len(gaps)} significant gaps (>{gap_threshold/60:.1f} min):")
    for gap in gaps:
        print(f"  {gap['start']} -> {gap['end']} ({gap['duration']:.1f} minutes)")
else:
    print("No significant time gaps found in the data")

print()

# Check if flight ends in descent (landing) or just stops
altitude_points = [track for track in sorted_tracks[-20:] if track.get('alt')]
if altitude_points:
    final_altitudes = [int(track['alt']) for track in altitude_points]
    print(f"Final altitude progression: {final_altitudes}")
    if final_altitudes[-1] < 1000:
        print("✅ Flight appears to end with landing (low altitude)")
    else:
        print(f"❌ Flight ends at cruise altitude ({final_altitudes[-1]} ft) - likely incomplete data")
else:
    print("No altitude data in final points")