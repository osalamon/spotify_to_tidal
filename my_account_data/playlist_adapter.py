import json
import glob
import os

def adapt_playlists():
    files = glob.glob("Playlist*.json")
    if not files:
        print("!!! Error: No 'Playlist*.json' files found.")
        return

    print(f">>> Found {len(files)} playlist files.")

    converted_data = {}
    total_tracks = 0
    skipped_podcasts = 0

    for f_path in files:
        with open(f_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        playlists = data.get('playlists', [])
        
        for pl in playlists:
            pl_name = pl.get('name')
            items = pl.get('items', [])
            
            if not items:
                continue
                
            clean_tracks = []
            for item in items:
                # --- THE FIX ---
                # 1. Check if 'track' exists and is not None (skips podcasts)
                track_obj = item.get('track')
                if track_obj is None:
                    skipped_podcasts += 1
                    continue
                
                # 2. Extract data from inside the 'track' object
                track_name = track_obj.get('trackName')
                artist_name = track_obj.get('artistName')
                album_name = track_obj.get('albumName', '')

                if track_name and artist_name:
                    clean_tracks.append({
                        "artist": artist_name,
                        "title": track_name,
                        "album": album_name
                    })

            if clean_tracks:
                converted_data[pl_name] = clean_tracks
                total_tracks += len(clean_tracks)
                print(f"    Loaded: {pl_name} ({len(clean_tracks)} tracks)")

    # Output
    out_file = "spotify_actual_playlists.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=4)

    print(f"\n>>> SUCCESS.")
    print(f">>> Extracted {total_tracks} MUSIC tracks (Skipped {skipped_podcasts} podcasts).")
    print(f">>> Saved to: {out_file}")

if __name__ == "__main__":
    adapt_playlists()