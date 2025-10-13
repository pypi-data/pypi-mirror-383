#!/usr/bin/env python3
"""
Test UA1584 to see if it has complete flight tracking data
"""
import os
from pyfr24 import FR24API

# Initialize API
token = os.environ.get("FLIGHTRADAR_API_KEY")
api = FR24API(token)

print("=== TESTING UA1584 FOR COMPLETE FLIGHT DATA ===")
print()

flight_number = "UA1584"
date = "2025-08-02"  # Assuming same date, let me know if different

print(f"Looking up {flight_number} on {date}...")

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
        print("❌ No flight data found for UA1584 on this date")
        print("Please provide the correct date for UA1584")
        exit()
        
    print(f"Found {len(data)} flight instance(s):")
    print()
    
    for i, flight in enumerate(data):
        flight_id = flight.get('fr24_id', 'N/A')
        origin = flight.get('orig_icao', 'N/A')
        dest = flight.get('dest_icao', 'N/A')
        takeoff = flight.get('datetime_takeoff', 'N/A')
        landed = flight.get('datetime_landed', 'N/A')
        
        print(f"=== Flight {i+1}: {flight_id} ===")
        print(f"Route: {origin} -> {dest}")
        print(f"Takeoff: {takeoff}")
        print(f"Landed: {landed}")
        print()
        
        # Get tracks
        print("Getting flight tracks...")
        tracks_data = api.get_flight_tracks(flight_id)
        if isinstance(tracks_data, list) and tracks_data:
            tracks = tracks_data[0].get("tracks", [])
        elif isinstance(tracks_data, dict):
            tracks = tracks_data.get("tracks", [])
        else:
            tracks = []
            
        if not tracks:
            print("❌ No tracks available")
            continue
            
        sorted_tracks = sorted(tracks, key=lambda x: x.get("timestamp", ""))
        
        print(f"📊 Track Analysis:")
        print(f"  Total points: {len(sorted_tracks)}")
        print(f"  First: {sorted_tracks[0].get('timestamp')}")
        print(f"  Last: {sorted_tracks[-1].get('timestamp')}")
        
        # Calculate flight duration if both times available
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
                
                if tracked_duration / planned_duration > 0.9:  # More than 90% coverage
                    print(f"  ✅ APPEARS COMPLETE")
                elif tracked_duration / planned_duration > 0.8:  # 80-90% coverage
                    print(f"  ⚠️  MOSTLY COMPLETE")
                else:
                    print(f"  ❌ INCOMPLETE")
                    
            except Exception as e:
                print(f"  Error calculating duration: {e}")
        elif landed == 'N/A':
            print(f"  ⚠️  No landing time in summary - might be incomplete")
        
        # Check final position and altitude
        last_track = sorted_tracks[-1]
        if 'lat' in last_track and 'lon' in last_track:
            final_lat, final_lon = float(last_track['lat']), float(last_track['lon'])
            final_alt = last_track.get('alt', 'N/A')
            print(f"  Final position: {final_lat:.2f}, {final_lon:.2f}")
            print(f"  Final altitude: {final_alt} ft")
            
            # Check if at ground level (complete landing)
            if isinstance(final_alt, (int, float, str)) and str(final_alt).replace('-', '').isdigit():
                alt_num = int(final_alt)
                if alt_num < 1000:  # Low altitude = likely landed
                    print(f"  ✅ LANDED - Low final altitude")
                elif alt_num > 25000:  # High altitude = likely incomplete
                    print(f"  ❌ INCOMPLETE - Still at cruise altitude")
                else:
                    print(f"  ⚠️  INTERMEDIATE ALTITUDE")
        
        print()
        
        # If this looks complete, let's test our visualization
        if len(sorted_tracks) > 0:
            print("🎯 ATTEMPTING VISUALIZATION TEST...")
            try:
                # Test with our smart-export (using the local version)
                import subprocess
                cmd = [
                    "./pyfr24-cli", "smart-export", 
                    "--flight", flight_number, 
                    "--date", date,
                    "--auto-select", "latest",
                    "--output-dir", f"test_ua1584_output"
                ]
                
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print("✅ Visualization completed successfully!")
                    print("Check the test_ua1584_output directory for results")
                else:
                    print(f"❌ Visualization failed:")
                    print(f"STDOUT: {result.stdout}")
                    print(f"STDERR: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("⏰ Visualization timed out")
            except Exception as e:
                print(f"❌ Visualization error: {e}")
        
        print("=" * 50)
        
except Exception as e:
    print(f"Error: {e}")

print("\n🔍 UA1584 Analysis Complete")
print("If this flight shows complete coverage, we'll know the API")
print("CAN provide full flight paths for some flights.")