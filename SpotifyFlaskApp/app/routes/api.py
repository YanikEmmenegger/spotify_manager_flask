from flask import Blueprint, jsonify
from app.services.spotify_service import SpotifyService
from app.services.db_service import DBService

bp = Blueprint('api', __name__)

spotify_service = SpotifyService()
db_service = DBService()


@bp.route('/save', methods=['GET'])
def save_spotify_data():
    active_users_response = db_service.get_active_users()
    if not active_users_response['success']:
        return jsonify(
            {"error": f"Error in save_spotify_data (get_active_users): {active_users_response['error']}"}), 500

    active_users = active_users_response['data']
    for user in active_users:
        access_token_response = spotify_service.exchange_refresh_token(user['spotify_key'])
        if not access_token_response['success']:
            return jsonify({
                "error": f"Error in save_spotify_data (exchange_refresh_token): {access_token_response['error']}"}), 500

        access_token = access_token_response['access_token']
        recently_played_response = spotify_service.get_recently_played(access_token)
        if not recently_played_response['success']:
            return jsonify({
                "error": f"Error in save_spotify_data (get_recently_played): {recently_played_response['error']}"}), 500

        for track in recently_played_response['data']['items']:
            insert_track_response = db_service.insert_track_into_recent(track['played_at'], user['spotify_uuid'],
                                                                        track['track'])
            if not insert_track_response['success']:
                return jsonify({
                    "error": f"Error in save_spotify_data (insert_track_into_recent): {insert_track_response['error']}"}), 500

    return jsonify({"message": "Spotify data saved successfully"}), 200


@bp.route('/topmix', methods=['GET'])
def update_topmix():
    active_users_response = db_service.get_active_users()
    if not active_users_response['success']:
        return jsonify({"error": f"Error in update_topmix (get_active_users): {active_users_response['error']}"}), 500

    active_users = active_users_response['data']
    for user in active_users:
        access_token_response = spotify_service.exchange_refresh_token(user['spotify_key'])
        if not access_token_response['success']:
            return jsonify(
                {"error": f"Error in update_topmix (exchange_refresh_token): {access_token_response['error']}"}), 500

        access_token = access_token_response['access_token']
        top_tracks_response = db_service.get_listened_to(None, None, user['spotify_uuid'])
        if not top_tracks_response['success']:
            return jsonify({"error": f"Error in update_topmix (get_listened_to): {top_tracks_response['error']}"}), 500

        top_tracks_sorted = spotify_service.create_sorted_collection(top_tracks_response['data'], 70)
        playlist_id_response = spotify_service.get_or_create_playlist(access_token, "TOPMIX 14 Days",
                                                                      user['spotify_uuid'])
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
