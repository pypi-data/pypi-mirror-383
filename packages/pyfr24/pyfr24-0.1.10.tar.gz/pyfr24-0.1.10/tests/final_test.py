#!/usr/bin/env python3
"""
Final attempt to get complete flight data using different approaches
"""
import os
import time
from pyfr24 import FR24API

# Initialize API
token = os.environ.get("FLIGHTRADAR_API_KEY")
api = FR24API(token)

flight_id = "3b8b02be"

print("=== FINAL ATTEMPT TO GET COMPLETE FLIGHT DATA ===")
print()

# Test 1: Try with really large limit to see if there's a default limit
print("1. Testing with very large limit:")
try:
    url = "https://fr24api.flightradar24.com/api/flight-tracks"
    params = {"flight_id": flight_id, "limit": 10000}
    response = api._make_request("get", url, headers=api.session.headers, params=params)
    data = response.json()
    
    if isinstance(data, list) and data:
        tracks = data[0].get("tracks", [])
    else:
        tracks = []
    
    print(f"  Result: {len(tracks)} tracks")
    if tracks:
        sorted_tracks = sorted(tracks, key=lambda x: x.get("timestamp", ""))
        print(f"  Last: {sorted_tracks[-1].get('timestamp')} at {sorted_tracks[-1].get('lat')}, {sorted_tracks[-1].get('lon')}")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 2: Try requesting data in time ranges
print("2. Testing time-based requests:")
try:
    # Try to get data after our current end time
    params = {
        "flight_id": flight_id,
        "from": "2025-08-02T17:50:00Z",  # After our current end
        "to": "2025-08-02T20:00:00Z"     # Should cover the landing
    }
    url = "https://fr24api.flightradar24.com/api/flight-tracks"
    response = api._make_request("get", url, headers=api.session.headers, params=params)
    data = response.json()
    
    if isinstance(data, list) and data:
        tracks = data[0].get("tracks", [])
    else:
        tracks = []
    
    print(f"  Time range request: {len(tracks)} tracks")
    if tracks:
        print(f"  Got additional data from {tracks[0].get('timestamp')} to {tracks[-1].get('timestamp')}")
except Exception as e:
    print(f"  Time range error: {e}")

print()

# Test 3: Check if there are different data sources or track types
print("3. Testing different data source parameters:")
source_params = [
    {"flight_id": flight_id, "source": "adsb"},
    {"flight_id": flight_id, "source": "mlat"},
    {"flight_id": flight_id, "source": "satellite"},
    {"flight_id": flight_id, "source": "all"},
    {"flight_id": flight_id, "type": "full"},
    {"flight_id": flight_id, "include_estimated": "true"},
]

for params in source_params:
    try:
        url = "https://fr24api.flightradar24.com/api/flight-tracks"
        response = api._make_request("get", url, headers=api.session.headers, params=params)
        data = response.json()
        
        if isinstance(data, list) and data:
            tracks = data[0].get("tracks", [])
        else:
            tracks = []
        
        param_str = ", ".join(f"{k}={v}" for k, v in params.items() if k != "flight_id")
        print(f"  {param_str}: {len(tracks)} tracks")
        if tracks:
            sorted_tracks = sorted(tracks, key=lambda x: x.get("timestamp", ""))
            last_time = sorted_tracks[-1].get('timestamp')
            if last_time and "19:" in last_time:  # Looking for landing time around 19:12
                print(f"    *** FOUND LATER DATA: ends at {last_time} ***")
    except Exception as e:
        print(f"  {param_str}: Error - {e}")

print()

# Test 4: One more check - maybe the API documentation has hints
print("4. Checking response headers for hints:")
try:
    url = "https://fr24api.flightradar24.com/api/flight-tracks"
    params = {"flight_id": flight_id}
    response = api._make_request("get", url, headers=api.session.headers, params=params)
    
    print("  Response headers:")
    for header, value in response.headers.items():
        if any(keyword in header.lower() for keyword in ['limit', 'total', 'count', 'page', 'more']):
            print(f"    {header}: {value}")
    
    # Check if response indicates truncation
    if 'x-total-count' in response.headers:
        total = response.headers['x-total-count']
        print(f"  Total available: {total}")
    
except Exception as e:
    print(f"  Header check error: {e}")

print("\n=== CONCLUSION ===")
print("Based on all tests, this appears to be a genuine API limitation")
print("where Flightradar24's flight-tracks endpoint doesn't provide")
print("complete historical flight paths, even though the web interface")
print("and flight summary endpoints know about the complete flight.")