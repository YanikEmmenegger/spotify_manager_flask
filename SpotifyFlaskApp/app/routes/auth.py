from flask import Blueprint, redirect, request
from app.services.spotify_service import SpotifyService
from app.services.db_service import DBService

bp = Blueprint('auth', __name__)

spotify_service = SpotifyService()
db_service = DBService()


@bp.route('/')
def auth_index():
    auth_url = spotify_service.auth_manager.get_authorize_url()
    return redirect(auth_url)


@bp.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = spotify_service.get_access_token(code)
    if not token_info:
        return 'Failed to get access token', 500

    user_profile = spotify_service.get_user_profile(token_info['access_token'])
    if user_profile['success']:
        user = user_profile['data']
        insert_response = db_service.insert_user(user['id'], user['display_name'], True, token_info['refresh_token'])
        if insert_response['success']:
            return 'User profile retrieved successfully! - please close this tab'
    return 'Sorry, there was an error. Please try again.'
