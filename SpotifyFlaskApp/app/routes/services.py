# app/routes/services.py
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from app.routes.route_helper import get_tokens_from_headers
from app.services import SpotifyService, DBService

# Define the Blueprint
bp = Blueprint('services', __name__)

# Initialize services
spotify_service = SpotifyService()
db_service = DBService()


@bp.route('/save', methods=['POST'])
def save_spotify_data():
    try:
        refresh_token, spotify_uuid = get_tokens_from_headers()
        if not refresh_token or not spotify_uuid:
            return jsonify({"error": "Missing refresh token or Spotify UUID in headers"}), 400

        access_token_response = spotify_service.exchange_refresh_token(refresh_token)
        if not access_token_response['success']:
            return jsonify({
                "error": f"Error in save_spotify_data (exchange_refresh_token): {access_token_response['error']}"}), 500

        access_token = access_token_response['access_token']
        recently_played_response = spotify_service.get_recently_played(access_token)
        if not recently_played_response['success']:
            return jsonify({
                "error": f"Error in save_spotify_data (get_recently_played): {recently_played_response['error']}"}), 500

        for track in recently_played_response['data']['items']:
            insert_track_response = db_service.insert_track_into_recent(track['played_at'], spotify_uuid,
                                                                        track['track'])
            if not insert_track_response['success']:
                return jsonify({
                    "error": f"Error in save_spotify_data (insert_track_into_recent): {insert_track_response['error']}"}), 500

        return jsonify({"message": "Spotify data saved successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Error in save_spotify_data: {e}"}), 500


@bp.route('/topmix', methods=['POST'])
def update_topmix():
    try:
        refresh_token, spotify_uuid = get_tokens_from_headers()
        if not refresh_token or not spotify_uuid:
            return jsonify({"error": "Missing refresh token or Spotify UUID in headers"}), 400

        access_token_response = spotify_service.exchange_refresh_token(refresh_token)
        if not access_token_response['success']:
            return jsonify(
                {"error": f"Error in update_topmix (exchange_refresh_token): {access_token_response['error']}"}), 500

        access_token = access_token_response['access_token']

        topmix_exceptions_response = db_service.get_topmix_exceptions(spotify_uuid)
        if not topmix_exceptions_response['success']:
            return jsonify(
                {
                    "error": f"Error in update_topmix (get_topmix_exceptions): {topmix_exceptions_response['error']}"
                }), 500
        topmix_exceptions = topmix_exceptions_response['data']

        # create start and end date for the topmix
        # get the current date

        start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        top_tracks_response = db_service.get_listened_to(start_date, end_date, spotify_uuid, None,
                                                         topmix_exceptions['artists'],
                                                         topmix_exceptions['tracks'], None)
        if not top_tracks_response['success']:
            return jsonify({"error": f"Error in update_topmix (get_listened_to): {top_tracks_response['error']}"}), 500

        top_tracks_sorted = spotify_service.create_sorted_collection(top_tracks_response['data'], 60)
        playlist_id_response = spotify_service.get_or_create_playlist(access_token, "TOPMIX 14 Days", spotify_uuid)
        if not playlist_id_response['success']:
            return jsonify(
                {"error": f"Error in update_topmix (get_or_create_playlist): {playlist_id_response['error']}"}), 500

        playlist_id = playlist_id_response['data']
        replace_tracks_response = spotify_service.replace_tracks_in_playlist(access_token, playlist_id,
                                                                             top_tracks_sorted)
        if not replace_tracks_response['success']:
            return jsonify({
                "error": f"Error in update_topmix (replace_tracks_in_playlist): {replace_tracks_response['error']}"}), 500

        return jsonify({"message": "Topmix updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Error in update_topmix: {e}"}), 500