from dataclasses import dataclass
from functools import cache
from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag
import requests as r

def _get_soup(uri: str) -> BeautifulSoup:
    resp = r.get(uri)
    if not resp.ok:
        raise Exception(f'Failed to get uri "{uri}" - status code: {resp.status_code}')
    return BeautifulSoup(resp.text, 'html.parser')


class SpotifyException(Exception):
    pass

@dataclass
class SpotifyArtist:
    id: str
    name: str

@dataclass
class SpotifyAlbum:
    id: str
    name: str
    artist_ids: list[str]
    track_ids: list[str]

    @property
    def artists(self) -> list[SpotifyArtist]:
        return [_get_artist_by_id(artist_id) for artist_id in self.artist_ids]

@dataclass
class SpotifyTrack:
    id: str
    name: str
    artist_ids: list[str]
    album_id: str
    duration_ms: int
    track_number: int

    @property
    def album(self) -> SpotifyAlbum:
        return _get_album_by_id(self.album_id)

    @property
    def artists(self) -> list[SpotifyArtist]:
        return [_get_artist_by_id(artist_id) for artist_id in self.artist_ids]

@dataclass
class SpotifyPlaylist:
    id: str
    name: str
    description: str
    track_ids: list[str]

    @property
    def uri(self) -> str:
        return _id_to_uri('playlist', self.id)

    def tracks(self) -> list[SpotifyTrack]:
        return list(map(_get_track_by_id, self.track_ids))

class Spotify:

    def playlist(self, uri: str | None = None, playlist_id: str | None = None) -> SpotifyPlaylist:
        if uri:
            return _get_playlist(uri)
        if playlist_id:
            return _get_playlist(_id_to_uri('playlist', playlist_id))
        raise NotImplementedError

def _get_content(elem: PageElement) -> str:
    if isinstance(elem, Tag):
        return str(elem.get('content'))
    return elem.get_text()

def _get_meta(soup: BeautifulSoup, name: str, key: str = 'name') -> str:
    assert soup.head
    elem = soup.find(attrs={key: name})
    if not elem:
        raise Exception(f'Could not find meta element {key}: {name} in soup:\n{soup}')
    return _get_content(elem)

def _id_to_uri(topic: str, id: str) -> str:
    return f'https://open.spotify.com/{topic}/{id}'

def _uri_to_id(uri: str) -> tuple[str, str]:
    parts = uri.split('/')
    return (parts[-2], parts[-1])

@cache
def _get_track(uri: str) -> SpotifyTrack:
    soup = _get_soup(uri)
    name = _get_meta(soup, 'og:title', 'property')
    artist_ids = list(map(lambda x: x[1], map(_uri_to_id, map(_get_content, soup.find_all(attrs={'name': 'music:musician'})))))
    album_id = _uri_to_id(_get_meta(soup, 'music:album'))[1]
    duration_ms = int(_get_meta(soup, 'music:duration')) * 1000
    track_number = int(_get_meta(soup, 'music:album:track'))
    return SpotifyTrack(
        id = _uri_to_id(uri)[1],
        name = name,
        artist_ids = artist_ids,
        duration_ms = duration_ms,
        track_number = track_number,
        album_id = album_id
    )

@cache
def _get_playlist(uri: str) -> SpotifyPlaylist:
    soup = _get_soup(uri)
    assert soup.head
    results = soup.head.find_all(attrs={'name': 'music:song'})
    tracklist = list(map(lambda x: _uri_to_id(_get_content(x))[1], results))
    title = _get_meta(soup, 'og:title', 'property')
    description = _get_meta(soup, 'og:description', 'property')
    return SpotifyPlaylist(_uri_to_id(uri)[1], title, description, tracklist)

def _get_track_by_id(id: str) -> SpotifyTrack:
    return _get_track(_id_to_uri('track', id))

@cache
def _get_album(uri: str) -> SpotifyAlbum:
    soup = _get_soup(uri)
    assert soup.head
    title = _get_meta(soup, 'og:title', 'property')
    results = soup.head.find_all(attrs={'name': 'music:musician'})
    artist_ids = list(map(lambda x: _uri_to_id(_get_content(x))[1], results))
    results = soup.head.find_all(attrs={'name': 'music:song'})
    track_ids = list(map(lambda x: _uri_to_id(_get_content(x))[1], results))
    return SpotifyAlbum(
        id = _uri_to_id(uri)[1],
        name = title,
        artist_ids = artist_ids,
        track_ids = track_ids
    )

def _get_album_by_id(id: str) -> SpotifyAlbum:
    return _get_album(_id_to_uri('album', id))

@cache
def _get_artist(uri: str) -> SpotifyArtist:
    soup = _get_soup(uri)
    assert soup.head
    title = _get_meta(soup, 'og:title', 'property')
    return SpotifyArtist(
        id = _uri_to_id(uri)[1],
        name = title,
    )
    

def _get_artist_by_id(id: str) -> SpotifyArtist:
    return _get_artist(_id_to_uri('artist', id))
