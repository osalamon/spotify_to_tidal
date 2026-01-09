// --- CONFIGURATION ---
const TOKEN = "Bearer BQBirbzVE3PYboTnTJR-83Xx620dAd72zRf9S3h4KEyyNESizgI1g9Qm0maW5lv4zpFh2_qlTRY7HGiM6VUrJLzYMfRh1kgypxHgmyl0qR6N3iIPo_gtV8-IpBKfU2h1U5E5KqalWbgh4O8tL2hG9rfRNhegSJXe6M78O-T0Aze0kPbNY_pzAmO7uiW4m_o4Lnx15cfmlf6xSiTrr5EhcZtgPVjdW7pwbvyviJf4xf6z6mbwgeMLGACgTfhNd1pYFJbxmKwckdDdKahvjOdeWUz8Jzpx2rEchOWB4d66aV95W6AvRyLvCWRk-C-z3fZ2eb8hJZx7ILw2Gm0PGfjaG29700As0r3NS_RB12DN8hpoaPhFTRHrSRsK9C0YlWzhrK38v-p7x9-3"; // <--- PASTE TOKEN HERE
const DELAY_MS = 2500; // 2.5s delay to be safe

// --- THE ENGINE ---
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function fetchWithRetry(url) {
    let retries = 3;
    while (retries > 0) {
        try {
            console.log(`fetching: ${url}...`);
            const res = await fetch(url, {
                headers: { "Authorization": TOKEN }
            });

            if (res.status === 429) {
                const retryAfter = parseInt(res.headers.get("Retry-After")) || 10;
                console.warn(`Rate limited! Waiting ${retryAfter}s...`);
                await sleep((retryAfter + 1) * 1000);
                continue;
            }

            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (e) {
            console.error(e);
            retries--;
            await sleep(3000);
        }
    }
    return null;
}

async function getAllItems(initialUrl) {
    let items = [];
    let nextUrl = initialUrl;
    while (nextUrl) {
        const data = await fetchWithRetry(nextUrl);
        if (!data) break;
        items.push(...data.items);
        nextUrl = data.next;
        await sleep(DELAY_MS); // Be gentle
    }
    return items;
}

async function runHeist() {
    console.clear();
    console.log("%c Starting Console Heist...", "color: #0f0; font-size: 16px; font-weight: bold;");
    
    // 1. Get User ID
    const me = await fetchWithRetry('https://community.spotify.com/t5/Spotify-for-Developers/Unable-to-create-app-in-Spotify-Developer/td-p/5632122/page/2');
    if (!me) return console.error("Token invalid?");
    const userId = me.id;
    console.log(`Logged in as: ${userId}`);

    // 2. Get Playlists
    console.log(">>> Fetching Playlists...");
    const playlists = await getAllItems(`https://api.spotify.com/v1/users/${userId}/playlists?limit=50`);
    console.log(`>>> Found ${playlists.length} playlists.`);

    const fullDump = {};

    // 3. Get Tracks
    for (const [index, pl] of playlists.entries()) {
        console.log(`Processing [${index + 1}/${playlists.length}]: ${pl.name}`);
        
        // Skip Spotify's algorithmic playlists if you want (they often fail exporting)
        // if (pl.owner.id !== userId) continue; 

        const tracks = await getAllItems(`https://api.spotify.com/v1/playlists/${pl.id}/tracks?limit=50`);
        
        fullDump[pl.name] = tracks.map(t => {
            const tr = t.track;
            if (!tr) return null;
            return {
                artist: tr.artists.map(a => a.name).join(", "),
                title: tr.name,
                album: tr.album.name,
                isrc: tr.external_ids ? tr.external_ids.isrc : ""
            };
        }).filter(t => t); // Filter nulls
    }

    // 4. Download File
    console.log(">>> Heist Complete. Downloading...");
    const blob = new Blob([JSON.stringify(fullDump, null, 2)], {type : 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `spotify_console_dump_${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

runHeist();