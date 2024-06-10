# app/helpers/spotify_helper.py
import logging
import time
import requests
from spotipy import SpotifyOAuth
from app.configs import Config

SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"


def handle_rate_limit(response, func, *args, **kwargs):
    """
    Handle Spotify API rate limiting by retrying after the specified wait time.
    """
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', None))

        if retry_after is None:
            logging.error(f"Rate limited without Retry-After header: {response.headers}")
            return {'success': False, 'error': "Rate limited without Retry-After header"}

        logging.warning(f"Rate limited. Retrying after {retry_after} seconds")
        time.sleep(retry_after)
        return func(*args, **kwargs)
    if response.status_code == 404:
        return {'success': False, 'error': "Not Found"}
    return {'success': False, 'error': f"Failed: {response.reason}"}


def exchange_refresh_token(refresh_token):
    """
    Exchange the refresh token for a new access token.
    """
    try:
        auth_manager = SpotifyOAuth(
            client_id=Config.SPOTIPY_CLIENT_ID,
            client_secret=Config.SPOTIPY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIPY_REDIRECT_URI,
            scope=Config.SPOTIPY_SCOPES
        )
        auth_manager.refresh_access_token(refresh_token)
        access_token = auth_manager.get_access_token(as_dict=False)
        return {'success': True, 'access_token': access_token}
    except Exception as e:
        logging.error(f"Error exchanging refresh token: {e}")
        return {'success': False, 'error': f"Error occurred while exchanging refresh token: {e}"}


def make_spotify_api_request(access_token, endpoint, method='GET', data=None, params=None):
    """
    Make a request to the Spotify API.
    """
    try:
        url = f"{SPOTIFY_API_BASE_URL}/{endpoint}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = None

        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        else:
            return {'success': False, 'error': f"Unsupported HTTP method: {method}"}

        if response.status_code in [200, 201]:
            return {'success': True, 'data': response.json()}

        if response.status_code == 429:
            logging.debug(f"Headers: {response.headers}")
            return handle_rate_limit(response, make_spotify_api_request, access_token, endpoint, method, data, params)

        return {'success': False, 'error': f"Failed: {response.reason}"}
    except Exception as e:
        logging.error(f"Error making Spotify API request: {e}")
        return {'success': False, 'error': f"Error occurred while making Spotify API request: {e}"}


def get_current_user_profile(access_token):
    """
    Get the current user's profile information from Spotify.
    """
    return make_spotify_api_request(access_token, 'me')


def get_recently_played_songs(access_token):
    """
    Get the current user's recently played songs from Spotify.
    """
    return make_spotify_api_request(access_token, 'me/player/recently-played', params={'limit': 50})


def get_users_playlists(access_token, limit=50, offset=0):
    """
    Get the current user's playlists from Spotify.
    """
    playlists = []
    while True:
        response = make_spotify_api_request(access_token, 'me/playlists', params={'limit': limit, 'offset': offset})
        if response['success']:
            playlists.extend(response['data']['items'])
            if len(response['data']['items']) < limit:
                break
            offset += limit
        else:
            return response
    return {'success': True, 'data': playlists}


def get_playlist_id_by_name(access_token, playlist_name):
    """
    Get the ID of a playlist by its name.
    """
    playlists = get_users_playlists(access_token)
    if playlists['success']:
        for playlist in playlists['data']:
            if playlist['name'] == playlist_name:
                logging.info(f"Playlist found: {playlist_name}")
                return {'success': True, 'playlist_id': playlist['id']}
        logging.info(f"Playlist not found: {playlist_name}")
        return {'success': True, 'playlist_id': None}
    return playlists


def create_playlist(access_token, playlist_name, spotify_uuid):
    """
    Create a new playlist for the user.
    """
    data = {
        "name": playlist_name,
        "description": "Topmix playlist",
        "public": False
    }
    return make_spotify_api_request(access_token, f"users/{spotify_uuid}/playlists", method='POST', data=data)


def replace_tracks_in_playlist(access_token, playlist_id, track_ids):
    """
    Replace tracks in a playlist with a new set of tracks.
    """
    data = {"uris": track_ids}
    return make_spotify_api_request(access_token, f"playlists/{playlist_id}/tracks", method='PUT', data=data)


def create_sorted_collection(tracks, limit=50):
    """
    Create a sorted collection of tracks based on their frequency.
    """
    import collections
    track_counts = collections.Counter(entry['tid'] for entry in tracks)
    sorted_track_ids = [track_id for track_id, _ in track_counts.most_common(limit)]
    unique_tracks = ['spotify:track:' + track_id for track_id in sorted_track_ids]
    return unique_tracks


def get_artist_by_id(access_token, artist_id):
    """
    Get details of an artist by their ID.
    """
    return make_spotify_api_request(access_token, f"artists/{artist_id}")


def get_track_details(access_token, track_id):
    """
    Get audio features for a track by its ID.
    """
    return make_spotify_api_request(access_token, f"audio-features/{track_id}")
