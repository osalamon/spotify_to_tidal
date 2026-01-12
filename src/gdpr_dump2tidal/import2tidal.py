import json
import tidalapi
import os

path_to_archives = "../../extended-streaming-history/"
print(f">>> Path where you stored output file of parser.py: {path_to_archives}")

def tidal_import():
    print(">>> Logging into Tidal...")
    session = tidalapi.Session()
    # This will print a link to click. 
    session.login_oauth_simple()
    print(f">>> Logged in as: {session.user.first_name}")

    # Load Data
    try:
        with open(os.path.join(path_to_archives, "spotify_history-parsed_into_playlists.json"), "r", encoding="utf-8") as f:
            playlists = json.load(f)
    except FileNotFoundError:
        print("!!! Error: Run parser.py first.")
        return

    for pl_name, tracks in playlists.items():
        print(f"\n>>> Creating Playlist: {pl_name} ({len(tracks)} tracks)")
        
        # Create Playlist
        new_pl = session.user.create_playlist(pl_name, f"Recovered from Spotify History via Python")
        
        track_ids = []
        not_found = []

        print(f"    Searching Tidal...", end="", flush=True)
            
        for i, t in enumerate(tracks):
            if i % 10 == 0: print(".", end="", flush=True)
            
            # --- FIX 1: Smart Truncation for Medleys ---
            # If title is a slash-separated medley, take the first part
            clean_title = t['title']
            if "/" in clean_title:
                clean_title = clean_title.split("/")[0].strip()
            
            # Hard cap to prevent URL overflow (60 chars is plenty for search)
            if len(clean_title) > 60:
                clean_title = clean_title[:60].strip()

            search_query = f"{t['artist']} {clean_title}"
            
            try:
                # --- FIX 2: Catch Server Errors (500) ---
                results = session.search(search_query, models=[tidalapi.media.Track], limit=1)
            except Exception as e:
                # If Tidal crashes on a specific track, log it and keep moving
                print(f"\n    [API ERROR] Skipping '{search_query}': {e}")
                not_found.append(f"{t['artist']} - {t['title']} (Caused API Crash)")
                continue

            found = False
            # Check results (Standard logic follows...)
            if results['tracks']:
                track_ids.append(results['tracks'][0].id)
                found = True
            else:
                # Fuzzy fallback (try even simpler search)
                simple_title = clean_title.split('(')[0].strip()
                try:
                    res_retry = session.search(f"{t['artist']} {simple_title}", models=[tidalapi.media.Track], limit=1)
                    if res_retry['tracks']:
                        track_ids.append(res_retry['tracks'][0].id)
                        found = True
                except:
                    pass # If fallback fails, just mark not found
            
            if not found:
                not_found.append(f"{t['artist']} - {t['title']}")

        # Bulk Add
        if track_ids:
            new_pl.add(track_ids)
            print(f"\n    [OK] Added {len(track_ids)} tracks.")
        
        if not_found:
            print(f"    [MISSING] Could not find {len(not_found)} tracks:")
            # Save missing tracks to a log file for manual hunting
            with open(os.path.join(path_to_archives, "missing_tracks.log"), "a", encoding="utf-8") as log:
                log.write(f"\n--- {pl_name} ---\n")
                for nf in not_found:
                    log.write(nf + "\n")

    print("\n>>> MIGRATION COMPLETE.")

if __name__ == "__main__":
    tidal_import()
