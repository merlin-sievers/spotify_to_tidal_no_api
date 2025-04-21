import yaml
import argparse
import sys

from .type.config import GeneralConfig

from .sync import sync_playlists_wrapper, get_tidal_playlists_wrapper, pick_tidal_playlist_for_spotify_playlist,  \
                    get_playlists_from_config #, get_user_playlist_mappings, sync_favorites_wrapper
from .auth import open_tidal_session, open_spotify_session

def main():
    parser = argparse.ArgumentParser()
    _ = parser.add_argument('--config', default='config.yml', help='location of the config file')
    _ = parser.add_argument('--uri', help='synchronize a specific URI instead of the one in the config')
    _ = parser.add_argument('--sync-favorites', action=argparse.BooleanOptionalAction, help='synchronize the favorites')
    args = parser.parse_args()

    assert isinstance(args.config, str)  # pyright:ignore[reportAny]
    assert isinstance(args.uri, str) or args.uri is None  # pyright:ignore[reportAny]
    with open(args.config, 'r') as f:
        config: GeneralConfig = yaml.safe_load(f)  # pyright:ignore[reportAny]
    print("Opening Spotify session")
    spotify_session = open_spotify_session()
    print("Opening Tidal session")
    tidal_session = open_tidal_session()
    if not tidal_session.check_login():
        sys.exit("Could not connect to Tidal")
    if args.uri:
        # if a playlist ID is explicitly provided as a command line argument then use that
        spotify_playlist = spotify_session.playlist(args.uri)
        tidal_playlists = get_tidal_playlists_wrapper(tidal_session)
        tidal_playlist = pick_tidal_playlist_for_spotify_playlist(spotify_playlist, tidal_playlists)
        sync_playlists_wrapper(spotify_session, tidal_session, [tidal_playlist], config)
    elif config.get('sync_playlists', None):
        # if the config contains a sync_playlists list of mappings then use that
        sync_playlists_wrapper(spotify_session, tidal_session, get_playlists_from_config(spotify_session, tidal_session, config), config)

if __name__ == '__main__':
    main()
    sys.exit(0)
