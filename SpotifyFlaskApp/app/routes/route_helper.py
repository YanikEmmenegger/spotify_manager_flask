import logging
from flask import request
from app.services import DBService, SpotifyService

db_service = DBService()
spotify_service = SpotifyService()


def get_tokens_from_headers():
    try:
        token = request.headers.get('Authorization')
        if not token or len(token.split(' ')) != 2:
            # Log and return error if the token is missing or invalid
            logging.error("Missing or invalid token in headers")
            return {'success': False, 'error': "Missing or invalid token in headers"}

        token = token.split(' ')[1]
        # Check if token is valid in the database
        user = db_service.get_user_by_token(token)
        if not user['success']:
            logging.error(f"Invalid token: {user['error']}")
            return {'success': False, 'error': user['error']}

        user = user['data']
        access_token_response = spotify_service.exchange_refresh_token(token)
        if not access_token_response['success']:
            logging.error(f"Error (exchange_refresh_token): {access_token_response['error']}")
            return {
                'success': False, 'error': f"Error (exchange_refresh_token): {access_token_response['error']}"
            }, 500

        access_token = access_token_response['access_token']
        return {'success': True, 'access_token': access_token, 'spotify_uuid': user['spotify_uuid']}

    except Exception as e:
        logging.error(f"Error in get_tokens_from_headers: {e}")
        return {'success': False, 'error': f"Error in get_tokens_from_headers: {e}"}
