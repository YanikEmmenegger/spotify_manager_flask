from flask import request


def get_tokens_from_headers():
    refresh_token = request.headers.get('Authorization')
    spotify_uuid = request.headers.get('Spotify-UUID')
    if not refresh_token or not spotify_uuid:
        return None, None
    return refresh_token, spotify_uuid