#!/usr/bin/env python3
"""
Investigate the actual structure of the API response
"""
import os
import json
from pyfr24 import FR24API

# Initialize API
token = os.environ.get("FLIGHTRADAR_API_KEY")
api = FR24API(token)

flight_id = "3b8b02be"

print("=== INVESTIGATING API RESPONSE STRUCTURE ===")
print()

# Get raw response
raw_data = api.get_flight_tracks(flight_id)

print(f"Response type: {type(raw_data)}")
print(f"Response length: {len(raw_data) if isinstance(raw_data, list) else 'N/A'}")
print()

if isinstance(raw_data, list):
    print("RESPONSE IS A LIST!")
    for i, item in enumerate(raw_data):
        print(f"Item {i}: {type(item)}")
        if isinstance(item, dict):
            print(f"  Keys: {list(item.keys())}")
            if 'tracks' in item:
                print(f"  Tracks count: {len(item['tracks'])}")
                if item['tracks']:
                    print(f"  First track: {item['tracks'][0].get('timestamp')}")
                    print(f"  Last track: {item['tracks'][-1].get('timestamp')}")
            # Check for any other interesting keys
            for key, value in item.items():
                if key != 'tracks':
                    print(f"  {key}: {value}")
        print()

# Let's also check if our current parsing is missing some data
print("=== CHECKING OUR CURRENT PARSING ===")

# Current parsing logic from export_flight_data
if isinstance(raw_data, list):
    if len(raw_data) == 1 and isinstance(raw_data[0], dict) and "tracks" in raw_data[0]:
        tracks = raw_data[0]["tracks"]
        print("Using single dict with tracks")
    else:
        tracks = raw_data
        print("Using raw list as tracks")
elif isinstance(raw_data, dict):
    tracks = raw_data.get("tracks", [])
    print("Using dict.tracks")
else:
    tracks = []
    print("No valid tracks found")

print(f"Parsed tracks count: {len(tracks)}")

# Maybe there are multiple track segments?
if isinstance(raw_data, list) and len(raw_data) > 1:
    print("\n=== MULTIPLE SEGMENTS DETECTED ===")
    all_tracks = []
    for i, segment in enumerate(raw_data):
        if isinstance(segment, dict) and 'tracks' in segment:
            segment_tracks = segment['tracks']
            print(f"Segment {i}: {len(segment_tracks)} tracks")
            if segment_tracks:
                print(f"  First: {segment_tracks[0].get('timestamp')}")
                print(f"  Last: {segment_tracks[-1].get('timestamp')}")
            all_tracks.extend(segment_tracks)
        elif isinstance(segment, dict):
            # Maybe it's a direct track point
            if 'timestamp' in segment:
                all_tracks.append(segment)
                print(f"Segment {i}: Direct track point at {segment.get('timestamp')}")
    
    print(f"\nCOMBINED: {len(all_tracks)} total tracks")
    if all_tracks:
        sorted_all = sorted(all_tracks, key=lambda x: x.get('timestamp', ''))
        print(f"Combined first: {sorted_all[0].get('timestamp')}")
        print(f"Combined last: {sorted_all[-1].get('timestamp')}")
        
        # Check if this gives us more complete data
        last_track = sorted_all[-1]
        if 'lat' in last_track and 'lon' in last_track:
            final_lat, final_lon = float(last_track['lat']), float(last_track['lon'])
            atlanta_lat, atlanta_lon = 33.64, -84.43
            distance = ((final_lat - atlanta_lat)**2 + (final_lon - atlanta_lon)**2)**0.5
            print(f"Final position: {final_lat:.2f}, {final_lon:.2f}")
            print(f"Distance to Atlanta: ~{distance * 69:.0f} miles")
            
            if last_track.get('alt'):
                print(f"Final altitude: {last_track['alt']} ft")