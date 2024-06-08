# app/services/spotify_service.py
from app.helpers.spotify_helper import *
from spotipy.oauth2 import SpotifyOAuth
from app.configs import Config


class SpotifyService:
    def __init__(self):
        self.auth_manager = SpotifyOAuth(
            client_id=Config.SPOTIPY_CLIENT_ID,
            client_secret=Config.SPOTIPY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIPY_REDIRECT_URI,
            scope=Config.SPOTIPY_SCOPES
        )

    def get_access_token(self, code):
        try:
            return self.auth_manager.get_access_token(code)
        except Exception as e:
            logging.error(f"Error getting access token: {e}")
            return None

    @staticmethod
    def exchange_refresh_token(refresh_token):
        try:
            return exchange_refresh_token(refresh_token)
        except Exception as e:
            logging.error(f"Error exchanging refresh token: {e}")
            return {'success': False, 'error': f"Error exchanging refresh token: {e}"}

    @staticmethod
    def get_user_profile(access_token):
        try:
            return get_current_user_profile(access_token)
        except Exception as e:
            logging.error(f"Error getting user profile: {e}")
            return {'success': False, 'error': f"Error getting user profile: {e}"}

    @staticmethod
    def get_recently_played(access_token):
        try:
            return get_recently_played_songs(access_token)
        except Exception as e:
            logging.error(f"Error getting recently played songs: {e}")
            return {'success': False, 'error': f"Error getting recently played songs: {e}"}

    @staticmethod
    def create_sorted_collection(tracks, limit):
        try:
            return create_sorted_collection(tracks, limit)
        except Exception as e:
            logging.error(f"Error creating sorted collection: {e}")
            return {'success': False, 'error': f"Error creating sorted collection: {e}"}

    @staticmethod
    def get_or_create_playlist(access_token, playlist_name, spotify_uuid):
        try:
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
        except Exception as e:
            logging.error(f"Error getting or creating playlist: {e}")
            return {'success': False, 'error': f"Error getting or creating playlist: {e}"}

    @staticmethod
    def replace_tracks_in_playlist(access_token, playlist_id, track_ids):
        try:
            return replace_tracks_in_playlist(access_token, playlist_id, track_ids)
        except Exception as e:
            logging.error(f"Error replacing tracks in playlist: {e}")
            return {'success': False, 'error': f"Error replacing tracks in playlist: {e}"}

    @staticmethod
    def get_artist_by_id(access_token, artist_id):
        try:
            return get_artist_by_id(access_token, artist_id)
        except Exception as e:
            logging.error(f"Error getting artist by id: {e}")
            return {'success': False, 'error': f"Error getting artist by id: {e}"}

    @staticmethod
    def get_track_details(access_token, track_id):
        try:
            return get_track_details(access_token, track_id)
        except Exception as e:
            logging.error(f"Error getting track details: {e}")
            return {'success': False, 'error': f"Error getting track details: {e}"}
