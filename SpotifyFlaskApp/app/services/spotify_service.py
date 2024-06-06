from app.helpers.spotify_helper import *
from spotipy.oauth2 import SpotifyOAuth
from app.configs.config import Config


class SpotifyService:
    def __init__(self):
        self.auth_manager = SpotifyOAuth(
            client_id=Config.SPOTIPY_CLIENT_ID,
            client_secret=Config.SPOTIPY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIPY_REDIRECT_URI,
            scope=Config.SPOTIPY_SCOPES
        )

    def get_access_token(self, code):
        return self.auth_manager.get_access_token(code)

    def exchange_refresh_token(self, refresh_token):
        return exchange_refresh_token(refresh_token)

    def get_user_profile(self, access_token):
        return get_current_user_profile(access_token)

    def get_recently_played(self, access_token):
        return get_recently_played_songs(access_token)

    def create_sorted_collection(self, tracks, limit):
        return create_sorted_collection(tracks, limit)

    def get_or_create_playlist(self, access_token, playlist_name, spotify_uuid):
        response = get_playlist_id_by_name(access_token, playlist_name)
        if not response['success']:
            return response
        playlist_id = response['playlist_id']
        if not playlist_id:
            create_response = create_playlist(access_token, playlist_name, spotify_uuid)
            if not create_response['success']:
                return create_response
            playlist_id = create_response['data']['id']
        return {'success': True, 'data': playlist_id}

    def replace_tracks_in_playlist(self, access_token, playlist_id, track_ids):
        return replace_tracks_in_playlist(access_token, playlist_id, track_ids)

    def get_artist_by_id(self, access_token, artist_id):
        return get_artist_by_id(access_token, artist_id)

    def get_track_details(self, access_token, track_id):
        return get_track_details(access_token, track_id)
