from flask_restful import Resource, reqparse
from flask import redirect, request, jsonify
from app.services import SpotifyService, DBService

spotify_service = SpotifyService()
db_service = DBService()

class AuthResource(Resource):
    def get(self):
        try:
            auth_url = spotify_service.auth_manager.get_authorize_url()
            return redirect(auth_url)
        except Exception as e:
            return {"error": f"Error during auth_index: {e}"}, 500

class AuthCallbackResource(Resource):
    def get(self):
        try:
            code = request.args.get('code')
            if not code:
                return {"error": "Missing authorization code"}, 400

            token_info = spotify_service.get_access_token(code)
            if not token_info:
                return {"error": "Failed to get access token"}, 500

            user_profile = spotify_service.get_user_profile(token_info['access_token'])
            if user_profile['success']:
                user = user_profile['data']
                insert_response = db_service.insert_user(user['id'], user['display_name'], True,
                                                         token_info['refresh_token'])
                if insert_response['success']:
                    response = redirect('http://localhost:5173/')
                    response.set_cookie('refresh_token', token_info['refresh_token'], httponly=False, secure=False)
                    response.set_cookie('spotify_uuid', user['id'], httponly=False, secure=False)
                    return response

            return {"error": "Failed to retrieve user profile"}, 500

        except Exception as e:
            return {"error": f"Error during callback: {e}"}, 500
