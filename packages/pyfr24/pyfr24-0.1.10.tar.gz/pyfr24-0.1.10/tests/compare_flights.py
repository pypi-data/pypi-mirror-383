#!/usr/bin/env python3
"""
Compare DL562 with other flights to see what's different
"""
import os
from pyfr24 import FR24API

# Initialize API
token = os.environ.get("FLIGHTRADAR_API_KEY")
api = FR24API(token)

print("=== COMPARING FLIGHT DATA COMPLETENESS ===")
print()

# Test flights - add the ones that worked for you
test_flights = [
    {"flight": "DL562", "date": "2025-08-02", "expected_route": "KSEA-KATL"},
    {"flight": "AS227", "date": "2025-08-02", "expected_route": "KJFK-KSFO"},  # From your recent files
    {"flight": "SY8924", "date": "2025-08-02", "expected_route": "KBDL-KLAX"}, # From your recent files
]

def analyze_flight(flight_number, date, expected_route):
    print(f"=== {flight_number} on {date} ({expected_route}) ===")
    
    try:
        # Get flight summary
        flight_datetime_from = f"{date}T00:00:00Z"
        flight_datetime_to = f"{date}T23:59:59Z"
        
        summary = api.get_flight_summary_full(
            flights=flight_number, 
            flight_datetime_from=flight_datetime_from, 
            flight_datetime_to=flight_datetime_to
        )
        
        data = summary.get('data', [])
        if not data:
            print("No flight data found")
            return
            
        flight = data[0]  # Take first match
        flight_id = flight.get('fr24_id', 'N/A')
        origin = flight.get('orig_icao', 'N/A')
        dest = flight.get('dest_icao', 'N/A')
        takeoff = flight.get('datetime_takeoff', 'N/A')
        landed = flight.get('datetime_landed', 'N/A')
        
        print(f"Flight ID: {flight_id}")
        print(f"Route: {origin} -> {dest}")
        print(f"Takeoff: {takeoff}")
        print(f"Landed: {landed}")
        print()
        
        # Get tracks using standard method
        tracks_data = api.get_flight_tracks(flight_id)
        if isinstance(tracks_data, list) and tracks_data:
            tracks = tracks_data[0].get("tracks", [])
        elif isinstance(tracks_data, dict):
            tracks = tracks_data.get("tracks", [])
        else:
            tracks = []
            
        if not tracks:
            print("❌ No tracks available")
            return
            
        sorted_tracks = sorted(tracks, key=lambda x: x.get("timestamp", ""))
        
        print(f"📊 Track Analysis:")
        print(f"  Total points: {len(sorted_tracks)}")
        print(f"  First: {sorted_tracks[0].get('timestamp')}")
        print(f"  Last: {sorted_tracks[-1].get('timestamp')}")
        
        # Calculate flight duration from summary vs tracks
        if takeoff != 'N/A' and landed != 'N/A':
            from datetime import datetime
            try:
                takeoff_dt = datetime.fromisoformat(takeoff.replace('Z', '+00:00'))
                landed_dt = datetime.fromisoformat(landed.replace('Z', '+00:00'))
                planned_duration = (landed_dt - takeoff_dt).total_seconds() / 3600
                
                track_start = datetime.fromisoformat(sorted_tracks[0]['timestamp'].replace('Z', '+00:00'))
                track_end = datetime.fromisoformat(sorted_tracks[-1]['timestamp'].replace('Z', '+00:00'))
                tracked_duration = (track_end - track_start).total_seconds() / 3600
                
                print(f"  Planned duration: {planned_duration:.1f} hours")
                print(f"  Tracked duration: {tracked_duration:.1f} hours")
                print(f"  Coverage: {(tracked_duration/planned_duration)*100:.1f}%")
                
                if tracked_duration / planned_duration < 0.8:  # Less than 80% coverage
                    print(f"  ❌ INCOMPLETE - Missing {planned_duration - tracked_duration:.1f} hours")
                else:
                    print(f"  ✅ COMPLETE")
                    
            except Exception as e:
                print(f"  Error calculating duration: {e}")
        
        # Check final position
        last_track = sorted_tracks[-1]
        if 'lat' in last_track and 'lon' in last_track:
            final_lat, final_lon = float(last_track['lat']), float(last_track['lon'])
            final_alt = last_track.get('alt', 'N/A')
            print(f"  Final position: {final_lat:.2f}, {final_lon:.2f}")
            print(f"  Final altitude: {final_alt} ft")
            
            # Check if still at cruise altitude (likely incomplete)
            if isinstance(final_alt, (int, float, str)) and str(final_alt).isdigit():
                alt_num = int(final_alt)
                if alt_num > 25000:  # High altitude = likely incomplete
                    print(f"  ⚠️  Ends at cruise altitude - possibly incomplete")
        
        print()
        
        # Test different API parameters for this specific flight
        print(f"🔧 Testing API Parameters:")
        test_params = [
            {},  # baseline
            {"source": "satellite"},
            {"source": "all"},
            {"limit": 2000},
        ]
        
        max_tracks = len(tracks)
        best_params = "baseline"
        
        for params in test_params:
            try:
                url = "https://fr24api.flightradar24.com/api/flight-tracks"
                full_params = {"flight_id": flight_id, **params}
                response = api._make_request("get", url, headers=api.session.headers, params=full_params)
                data = response.json()
                
                if isinstance(data, list) and data:
                    test_tracks = data[0].get("tracks", [])
                else:
                    test_tracks = []
                
                param_str = str(params) if params else "baseline"
                print(f"  {param_str}: {len(test_tracks)} tracks")
                
                if len(test_tracks) > max_tracks:
                    max_tracks = len(test_tracks)
                    best_params = param_str
                    
            except Exception as e:
                print(f"  {params}: Error - {e}")
        
        if best_params != "baseline":
            print(f"  🎯 Best result: {best_params} with {max_tracks} tracks")
        
        print("=" * 50)
        print()
        
    except Exception as e:
        print(f"Error analyzing {flight_number}: {e}")
        print()

# Analyze all flights
for flight_info in test_flights:
    analyze_flight(flight_info["flight"], flight_info["date"], flight_info["expected_route"])

print("🔍 COMPARISON COMPLETE")
print("Look for patterns in:")
print("- Which flights have complete vs incomplete coverage")
print("- Whether certain API parameters work better for specific flights")
print("- If flight duration, route, or airline affects data completeness")