A command line tool for importing your Spotify playlists into Tidal. Due to various performance optimisations, it is particularly suited for periodic synchronisation of very large collections.

Installation
-----------
Clone this git repository and then run:

```bash
python3 -m pip install -e .
```

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
