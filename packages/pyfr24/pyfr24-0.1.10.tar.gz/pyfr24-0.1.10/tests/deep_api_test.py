#!/usr/bin/env python3
"""
Deep dive into API behavior to understand why we're missing data
"""
import os
import json
from pyfr24 import FR24API

# Initialize API
token = os.environ.get("FLIGHTRADAR_API_KEY")
api = FR24API(token)

flight_id = "3b8b02be"  # Our DL562 flight

print("=== DEEP API INVESTIGATION ===")
print(f"Flight ID: {flight_id}")
print()

# Test 1: Look at raw response structure
print("1. RAW API RESPONSE STRUCTURE:")
print("-" * 40)
try:
    raw_data = api.get_flight_tracks(flight_id)
    print(f"Response type: {type(raw_data)}")
    print(f"Response keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dict'}")
    
    if isinstance(raw_data, dict):
        for key, value in raw_data.items():
            if key == 'tracks':
                print(f"  {key}: {type(value)} with {len(value) if isinstance(value, list) else 'unknown'} items")
            else:
                print(f"  {key}: {type(value)} = {value}")
    print()
    
    # Check if there are pagination hints in the response
    if isinstance(raw_data, dict):
        pagination_keys = ['total', 'count', 'page', 'next', 'has_more', 'continuation', 'offset', 'limit']
        found_pagination = {k: v for k, v in raw_data.items() if k in pagination_keys}
        if found_pagination:
            print(f"PAGINATION HINTS FOUND: {found_pagination}")
        else:
            print("No obvious pagination hints in response")
    print()
    
except Exception as e:
    print(f"Error: {e}")

# Test 2: Try different API parameters that might affect data range
print("2. TESTING DIFFERENT API PARAMETERS:")
print("-" * 40)

test_params = [
    {"flight_id": flight_id},  # baseline
    {"flight_id": flight_id, "format": "json"},
    {"flight_id": flight_id, "full": "true"},
    {"flight_id": flight_id, "complete": "true"},
    {"flight_id": flight_id, "all": "true"},
    {"flight_id": flight_id, "limit": 2000},
    {"flight_id": flight_id, "offset": 0, "limit": 2000},
]

for i, params in enumerate(test_params):
    print(f"Test {i+1}: {params}")
    try:
        url = "https://fr24api.flightradar24.com/api/flight-tracks"
        response = api._make_request("get", url, headers=api.session.headers, params=params)
        data = response.json()
        
        if isinstance(data, dict) and "tracks" in data:
            tracks = data["tracks"]
        elif isinstance(data, list) and len(data) > 0 and "tracks" in data[0]:
            tracks = data[0]["tracks"]
        else:
            tracks = []
            
        print(f"  Result: {len(tracks)} tracks")
        if tracks:
            print(f"    First: {tracks[0].get('timestamp', 'N/A')}")
            print(f"    Last:  {tracks[-1].get('timestamp', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

# Test 3: Check if there are other endpoints for flight tracks
print("3. TESTING ALTERNATIVE ENDPOINTS:")
print("-" * 40)

alternative_endpoints = [
    "https://fr24api.flightradar24.com/api/flight-tracks/full",
    "https://fr24api.flightradar24.com/api/flight-tracks/complete", 
    "https://fr24api.flightradar24.com/api/flight-tracks/all",
    "https://fr24api.flightradar24.com/api/flights/{}/tracks".format(flight_id),
    "https://fr24api.flightradar24.com/api/v1/flight-tracks",
]

for endpoint in alternative_endpoints:
    print(f"Testing: {endpoint}")
    try:
        params = {"flight_id": flight_id}
        response = api._make_request("get", endpoint, headers=api.session.headers, params=params)
        data = response.json()
        print(f"  Success! Response type: {type(data)}")
        if isinstance(data, dict):
            print(f"  Keys: {list(data.keys())}")
    except Exception as e:
        print(f"  Failed: {e}")
    print()

# Test 4: Look for any hints about data completeness in our current response
print("4. ANALYZING CURRENT DATA FOR COMPLETENESS HINTS:")
print("-" * 40)

data = api.get_flight_tracks(flight_id)
if isinstance(data, dict) and "tracks" in data:
    tracks = data["tracks"]
    
    # Check metadata
    metadata = {k: v for k, v in data.items() if k != 'tracks'}
    if metadata:
        print(f"Metadata found: {metadata}")
    
    # Check track data structure for hints
    if tracks:
        sample_track = tracks[0]
        print(f"Sample track keys: {list(sample_track.keys())}")
        
        # Look for any fields that might indicate data quality/completeness
        quality_fields = ['quality', 'source', 'confidence', 'complete', 'partial']
        found_quality = {k: v for k, v in sample_track.items() if any(qf in k.lower() for qf in quality_fields)}
        if found_quality:
            print(f"Quality indicators: {found_quality}")

print("\n=== SUMMARY ===")
print("If alternative endpoints work or show different data,")
print("we've found the issue. If not, we need to investigate")
print("whether this is a known API limitation or if there are")
print("authentication/permission issues.")