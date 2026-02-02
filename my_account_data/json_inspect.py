import json
import glob

files = glob.glob("Playlist*.json")
if not files:
    print("No playlist files found.")
    exit()

f_path = files[0]
print(f">>> Inspecting: {f_path}")

with open(f_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Check Root Type
print(f"ROOT Type: {type(data)}")
if isinstance(data, dict):
    print(f"ROOT Keys: {list(data.keys())}")
    
    # 2. Check Playlists
    playlists = data.get('playlists')
    if playlists and isinstance(playlists, list) and len(playlists) > 0:
        first_pl = playlists[0]
        print(f"\nSAMPLE PLAYLIST KEYS: {list(first_pl.keys())}")
        
        # 3. Check Items (Tracks)
        items = first_pl.get('items')
        if items and len(items) > 0:
            first_item = items[0]
            print(f"\nSAMPLE TRACK OBJECT:\n{json.dumps(first_item, indent=2)}")
        else:
            print("\n!!! First playlist has no items or 'items' key is missing.")
    else:
        print("\n!!! 'playlists' key is empty or not a list.")

elif isinstance(data, list):
    print("ROOT is a LIST (Unusual for Playlist1.json)")
    if len(data) > 0:
        print(f"SAMPLE ITEM: {data[0]}")