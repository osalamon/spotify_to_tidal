// --- CONFIGURATION ---
const TOKEN = "Bearer BQCPLHz5t-Sogils15QH6h2HPeoZq_KoOzuwhHtel4HxVwACuK62SHo9HfYAd4djj_m8P7T-YroWlLLpcsR2o4qRmZndqlxtWOUwCbTT6vYeES-k9SfzgHYF2xLv7wzQ_Z2s8cROq9cT5gMQgIi3qw1hlOOrXOpB60PiJaMq1lW8BF1YdacF7TbqHDqxBrf2idC119HAMO1sf2vqtsL6nRQHNpM4XS2aNgQ7mOLYsPJd_s-bCQwxtmOvCwBAJM3R_EARNQhErF8z8t4qvlVwGzcV8299aECJ8srSHmC9jgYx21EIaoxZ6QjO4mtrYLvDwyg68UL5wts8lttihoKlAaqtzlApc4XRf-4-Yh98AhUQhnGuguh5WpYof5LGiy_If6Nk9HVHAHge"; // <--- PASTE NEW TOKEN HERE
const DELAY_MS = 2500; // Keep it slow to avoid the '429' hammer

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
        await sleep(DELAY_MS);
    }
    return items;
}

async function runHeist() {
    console.clear();
    console.log("%c Starting Console Heist v2...", "color: #0f0; font-size: 16px; font-weight: bold;");
    
    // 1. Get User ID
    const me = await fetchWithRetry('https://api.spotify.com/v1/me');
    if (!me) return console.error("Token invalid? Did you copy the whole 'Bearer ...' string?");
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
        }).filter(t => t); 
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