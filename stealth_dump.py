import requests
import json
import time
import random

# --- CONFIGURATION ---
# 1. Open Spotify Web Player (F12 -> Network -> Refresh)
# 2. Copy the TOKEN (Bearer ...)
# SPOTIFY_TOKEN = "Bearer BQD......." 

SPOTIFY_TOKEN = "Bearer BQBirbzVE3PYboTnTJR-83Xx620dAd72zRf9S3h4KEyyNESizgI1g9Qm0maW5lv4zpFh2_qlTRY7HGiM6VUrJLzYMfRh1kgypxHgmyl0qR6N3iIPo_gtV8-IpBKfU2h1U5E5KqalWbgh4O8tL2hG9rfRNhegSJXe6M78O-T0Aze0kPbNY_pzAmO7uiW4m_o4Lnx15cfmlf6xSiTrr5EhcZtgPVjdW7pwbvyviJf4xf6z6mbwgeMLGACgTfhNd1pYFJbxmKwckdDdKahvjOdeWUz8Jzpx2rEchOWB4d66aV95W6AvRyLvCWRk-C-z3fZ2eb8hJZx7ILw2Gm0PGfjaG29700As0r3NS_RB12DN8hpoaPhFTRHrSRsK9C0YlWzhrK38v-p7x9-3"  # <--- YOUR STOLEN TOKEN

# 3. CRITICAL: Copy your User-Agent from the browser network tab (Request Headers)
#    (The one below is a generic Firefox one, but using your REAL one is safer)
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"

USER_ID = "ia0n488sfi356i6hwccdf9k88" # Ensure this is your actual username ID

# --- HEADERS (The Disguise) ---
headers = {
    "Authorization": SPOTIFY_TOKEN,
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://open.spotify.com",
    "Referer": "https://open.spotify.com/"
}

def make_request_with_retry(url):
    """
    Handles 429 Rate Limits with exponential backoff and anger management.
    """
    attempt = 0
    max_retries = 5
    
    while attempt < max_retries:
        # Sleep a tiny bit to avoid being robotic
        time.sleep(random.uniform(0.5, 2.0))
        
        print(f"[{attempt+1}] Hitting: {url[:60]}...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
            
        if response.status_code == 429:
            # They caught us. Check if they gave us a specific timeout.
            retry_after = int(response.headers.get("Retry-After", 10))
            # Add some buffer just to be safe
            wait_time = retry_after + random.randint(1, 5)
            
            print(f"!!! RATE LIMITED. Cooling down for {wait_time}s...")
            time.sleep(wait_time)
            attempt += 1
            continue
            
        # Other errors (401 = Token Expired, 403 = Forbidden)
        print(f"Error {response.status_code}: {response.text}")
        if response.status_code == 401:
            print(">>> YOUR TOKEN EXPIRED. Go steal a fresh one.")
            exit()
        return None

    print(">>> Max retries exceeded. Giving up on this batch.")
    return None

def get_all_playlists(user_id):
    playlists = []
    # Note: limit=50 is safer than 100 to fly under radar
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists?limit=50"
    
    while url:
        data = make_request_with_retry(url)
        if not data:
            break
            
        playlists.extend(data['items'])
        url = data['next']
        
    return playlists

def get_playlist_tracks(playlist_id):
    tracks = []
    # Only fetching what we need to minimize payload size
    fields = "items(track(name,artists(name),album(name),external_ids)),next"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields={fields}&limit=50"
    
    while url:
        data = make_request_with_retry(url)
        if not data:
            break
            
        for item in data['items']:
            if item and item.get('track'):
                tr = item['track']
                tracks.append({
                    "artist": tr['artists'][0]['name'] if tr['artists'] else "Unknown",
                    "title": tr['name'],
                    "album": tr['album']['name'] if tr['album'] else "Unknown",
                    "isrc": tr.get('external_ids', {}).get('isrc', '')
                })
        url = data['next']
        
    return tracks

# --- MAIN ---
print(">>> Starting Stealth Heist v2...")

# 1. Get Playlists
all_pl = get_all_playlists(USER_ID)
print(f">>> Found {len(all_pl)} playlists.")

full_dump = {}

# 2. Get Tracks (One by one, nice and slow)
for i, pl in enumerate(all_pl):
    print(f"\nProcessing {i+1}/{len(all_pl)}: {pl['name']}")
    tracks = get_playlist_tracks(pl['id'])
    full_dump[pl['name']] = tracks
    
    # Extra pause between playlists
    time.sleep(2) 

# 3. Save
with open('spotify_stealth_dump.json', 'w', encoding='utf-8') as f:
    json.dump(full_dump, f, ensure_ascii=False, indent=4)

print("\n>>> Done. 'spotify_stealth_dump.json' is ready.")