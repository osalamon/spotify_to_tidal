## PERSONAL NOTE

### IIUC, those motherfuckers from Spotify has restricted brutally access to their API.

I won't link their blog post where they stated that. If you hadn't created app in their Developers' Dashboard, you are probably screwed if you need your own API key.

But, if you just want to get your own data, there might be a way... Spotify webplayer has to have an authorization of some sort, don't you think? If you have Spotify account as their *client*, you are basically *bearer* of their shitty corporate ([predatory behavior](https://ra.co/news/80514)).

Yep, it's like that.

If someone has a bit of integrity, she or he may consider to inform their *network* of friends - from nerdy *devs* to normies. Yes, you can do it, even now. Just go and open all possible *tabs* of your chat *tools*, messengers, etc.

---

### TO WHOM IT MAY CONCERN

> Dear Spotify,
> 
> I hope you are enjoying being a submissive slave of Universal Music and similar shitty thieves. There's nothing I can do with it...
> 
> Except a little vent.
> 
> **If you decided to go the "Gordon Gekko" way, if you really wouldn't give people the steam of your piss... just GO FUCK YOURSELF!**
>
> KR, Ondrej

> PS: And all employees of Spotify should feel ashamed.

(I wouldn't expect such a bullshit from a company with origins in Sweden. Shame.)

---

## If someone still don't get it, simply put:

#### If you find a local non-mainstream band/project with less than 1.000 listens and you stream them on repeat, **Spotify takes your subscription money and gives it to fucking Taylor Swift or a major label fund.** 

## You are effectively subsidizing the pop music you don't listen to.

---

## Original README.md of ([**`spotify_to_tidal`**](https://github.com/spotify2tidal/spotify_to_tidal)) below:

---

A command line tool for importing your Spotify playlists into Tidal. Due to various performance optimisations, it is particularly suited for periodic synchronisation of very large collections.

Installation
-----------
Clone this git repository and then run:

```bash
python3 -m pip install -e .
```

Setup
-----
0. Rename the file example_config.yml to config.yml
0. Go [here](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/) and register a new app on developer.spotify.com.
0. Copy and paste your client ID and client secret to the Spotify part of the config file
0. Copy and paste the value in 'redirect_uri' of the config file to Redirect URIs at developer.spotify.com and press ADD
0. Enter your Spotify username to the config file

Usage
----
To synchronize all of your Spotify playlists with your Tidal account run the following from the project root directory
Windows ignores python module paths by default, but you can run them using `python3 -m spotify_to_tidal`

```bash
spotify_to_tidal
```

You can also just synchronize a specific playlist by doing the following:

```bash
spotify_to_tidal --uri 1ABCDEqsABCD6EaABCDa0a # accepts playlist id or full playlist uri
```

or sync just your 'Liked Songs' with:

```bash
spotify_to_tidal --sync-favorites
```

See example_config.yml for more configuration options, and `spotify_to_tidal --help` for more options.

---

#### Join our amazing community as a code contributor
<br><br>
<a href="https://github.com/spotify2tidal/spotify_to_tidal/graphs/contributors">
  <img class="dark-light" src="https://contrib.rocks/image?repo=spotify2tidal/spotify_to_tidal&anon=0&columns=25&max=100&r=true" />
</a>
