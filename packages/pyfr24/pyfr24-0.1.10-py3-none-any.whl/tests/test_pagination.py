#!/usr/bin/env python3
"""
Quick test to see if flight-tracks API supports pagination
"""
import os
from pyfr24 import FR24API

# Initialize API
token = os.environ.get("FLIGHTRADAR_API_KEY")
if not token:
    print("FLIGHTRADAR_API_KEY environment variable not set")
    exit(1)

api = FR24API(token)

flight_id = "3b8b02be"  # Our DL562 flight

print("Testing pagination parameters with flight-tracks API...")
print(f"Flight ID: {flight_id}")
print()

# Test 1: Standard call (what we're doing now)
print("1. Standard call (no pagination):")
try:
    data1 = api.get_flight_tracks(flight_id)
    if isinstance(data1, dict) and "tracks" in data1:
        tracks1 = data1["tracks"]
    elif isinstance(data1, list):
        tracks1 = data1[0]["tracks"] if data1 else []
    else:
        tracks1 = []
    print(f"   Got {len(tracks1)} track points")
    if tracks1:
        print(f"   First: {tracks1[0].get('timestamp', 'N/A')}")
        print(f"   Last:  {tracks1[-1].get('timestamp', 'N/A')}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 2: Try with offset/limit parameters
print("2. With pagination parameters (offset=0, limit=1000):")
try:
    # Manually make request with pagination params
    url = "https://fr24api.flightradar24.com/api/flight-tracks"
    params = {
        "flight_id": flight_id,
        "offset": 0,
        "limit": 1000
    }
    response = api._make_request("get", url, headers=api.session.headers, params=params)
    data2 = response.json()
    
    if isinstance(data2, dict) and "tracks" in data2:
        tracks2 = data2["tracks"]
    elif isinstance(data2, list):
        tracks2 = data2[0]["tracks"] if data2 else []
    else:
        tracks2 = []
    print(f"   Got {len(tracks2)} track points")
    if tracks2:
        print(f"   First: {tracks2[0].get('timestamp', 'N/A')}")
        print(f"   Last:  {tracks2[-1].get('timestamp', 'N/A')}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 3: Try with different offset
print("3. With offset=500 to get next page:")
try:
    url = "https://fr24api.flightradar24.com/api/flight-tracks"
    params = {
        "flight_id": flight_id,
        "offset": 500,
        "limit": 1000
    }
    response = api._make_request("get", url, headers=api.session.headers, params=params)
    data3 = response.json()
    
    if isinstance(data3, dict) and "tracks" in data3:
        tracks3 = data3["tracks"]
    elif isinstance(data3, list):
        tracks3 = data3[0]["tracks"] if data3 else []
    else:
        tracks3 = []
    print(f"   Got {len(tracks3)} track points")
    if tracks3:
        print(f"   First: {tracks3[0].get('timestamp', 'N/A')}")
        print(f"   Last:  {tracks3[-1].get('timestamp', 'N/A')}")
except Exception as e:
    print(f"   Error: {e}")

print()
print("If the API supports pagination, test 2 and 3 should show different data ranges.")