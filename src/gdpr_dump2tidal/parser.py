import json
import os
import glob
from collections import Counter, defaultdict
from datetime import datetime

# --- global config ---
SKIP_THRESHOLD_MS = 5 * 1000      # Only keep songs played > 5s
TOP_TRACKS_LIMIT = 1000           # Size of "Top of All Time" playlist
YEARLY_LIMIT = 2400               # Max size of yearly playlists
MONTHLY_LIMIT = 2000              # dtto of monthly playlists 

path_to_sptf_jsons = "../../extended-streaming-history/"
print(f">>> Path where you unzipped JSON files: {path_to_sptf_jsons}")

def parse_history():
    print(">>> Scanning for JSON files...")
    # Support both new (endsong) and old (Streaming_History) formats
    files = glob.glob(os.path.join(path_to_sptf_jsons, "endsong_*.json")) + glob.glob(os.path.join(path_to_sptf_jsons, "Streaming_History_Audio_*.json"))
    print(f">>> Found {len(files)} history files.")

    # Storage: "2023": Counter({"Artist - Track": 50})
    yearly_counts = defaultdict(Counter)
    monthly_counts = defaultdict(Counter)
    all_time_counts = Counter()
    
    # Metadata map to recover Album/ISRC later if needed (simple string matching for now)
    meta_map = {} 

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            # --- Normalize Keys (New vs Old format) ---
            track = item.get('master_metadata_track_name') or item.get('trackName')
            artist = item.get('master_metadata_album_artist_name') or item.get('artistName')
            ms_played = item.get('ms_played') or item.get('msPlayed', 0)
            ts_str = item.get('ts') or item.get('endTime') # '2023-10-14T...' or '2023-10-14 10:00'

            if not track or not artist or ms_played < SKIP_THRESHOLD_MS:
                continue

            # Create a unique key
            key = f"{artist} - {track}"
            
            # Parse Date info (Year and Month)
            try:
                # Handle both ISO and simple date formats
                dt = datetime.fromisoformat(ts_str.replace('Z', '')) 
                year = str(dt.year)
                month_str = f"{dt.year}-{dt.month:02d}"
            except (ValueError, TypeError):
                year = "Unknown_Year"
                month_str = "Unknown_Month"

            yearly_counts[year][key] += 1
            monthly_counts[month_str][key] += 1
            all_time_counts[key] += 1
            
            # Store clean metadata for the exporter
            if key not in meta_map:
                meta_map[key] = {
                    "artist": artist, 
                    "title": track,
                    "album": item.get('master_metadata_album_album_name', '')
                }

    print(">>> Parsing complete. Generating playlists...")
    
    final_playlists = {}

    # 1. Top of All Time
    top_all = [meta_map[k] for k, _ in all_time_counts.most_common(TOP_TRACKS_LIMIT)]
    final_playlists[f"ARCHIVE::: Top {TOP_TRACKS_LIMIT} All Time"] = top_all

    # 2. Yearly Archives
    for year, counter in sorted(yearly_counts.items()):
        # Filter for songs that were significant that year (e.g. played at least 2 times)
        significant_tracks = [meta_map[k] for k, count in counter.most_common(YEARLY_LIMIT) if count > 1]
        if significant_tracks:
            final_playlists[f"ARCHIVE::: Year {year}"] = significant_tracks
    
    # 3. Monthly Archives
    for month_str, counter in sorted(monthly_counts.items()):
        # filter tracks played once and more
        significant_tracks = [meta_map[k] for k, count in counter.most_common(MONTHLY_LIMIT) if count > 0]
        if significant_tracks:
            final_playlists[f"ARCHIVE::: {month_str}"] = significant_tracks

    # Output
    out_file = os.path.join(path_to_sptf_jsons, "spotify_history-parsed_into_playlists.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(final_playlists, f, indent=4)
        
    print(f">>> SUCCESS. Data saved to '{out_file}'")
    print(f">>> Created {len(final_playlists)} synthetic playlists.")

if __name__ == "__main__":
    parse_history()