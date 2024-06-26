import logging
from flask import Blueprint, jsonify
from app.services.spotify_service import SpotifyService
from app.services.db_service import DBService

# Define the Blueprint
bp = Blueprint('api', __name__)

# Initialize services
spotify_service = SpotifyService()
db_service = DBService()


@bp.route('/save', methods=['GET'])
def save_spotify_data():
    """
    Endpoint to save Spotify data for all active users.
    """
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
    """
    Endpoint to update the "Topmix" playlist for all active users.
    """
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


@bp.route('/update/artists', methods=['GET'])
def update_artists():
    """
    Endpoint to update artist information for incomplete artists.
    """
    active_users_response = db_service.get_active_users(1)
    if not active_users_response['success']:
        return jsonify({"error": f"Error in update_artists (get_active_users): {active_users_response['error']}"}), 500

    active_user = active_users_response['data'][0]
    access_token_response = spotify_service.exchange_refresh_token(active_user['spotify_key'])
    if not access_token_response['success']:
        return jsonify(
            {"error": f"Error in update_artists (exchange_refresh_token): {access_token_response['error']}"}), 500

    access_token = access_token_response['access_token']
    incomplete_artists_response = db_service.get_incomplete_artists()
    if not incomplete_artists_response['success']:
        return jsonify(
            {"error": f"Error in update_artists (get_incomplete_artists): {incomplete_artists_response['error']}"}), 500

    incomplete_artists = incomplete_artists_response['data']
    for artist in incomplete_artists:
        artist_id = artist['aid']
        artist_response = spotify_service.get_artist_by_id(access_token, artist_id)
        if not artist_response['success']:
            return jsonify({"error": f"Error in update_artists (get_artist_by_id): {artist_response['error']}"}), 500

        artist_data = artist_response['data']
        artist_image = artist_data['images'][0]['url'] if artist_data['images'] else None
        artist_genres = artist_data['genres']

        update_artist_response = db_service.update_artist(artist_id, artist_genres, artist_image)
        if not update_artist_response['success']:
            return jsonify(
                {"error": f"Error in update_artists (update_artist): {update_artist_response['error']}"}), 500

    return jsonify({"message": "Artists updated successfully"}), 200


@bp.route('/update/tracks', methods=['GET'])
def update_tracks():
    """
    Endpoint to update track information for incomplete tracks.
    """
    active_users_response = db_service.get_active_users(1)
    if not active_users_response['success']:
        return jsonify({"error": f"Error in update_tracks (get_active_users): {active_users_response['error']}"}), 500

    active_user = active_users_response['data'][0]
    access_token_response = spotify_service.exchange_refresh_token(active_user['spotify_key'])
    if not access_token_response['success']:
        return jsonify(
            {"error": f"Error in update_tracks (exchange_refresh_token): {access_token_response['error']}"}), 500

    access_token = access_token_response['access_token']
    incomplete_tracks_response = db_service.get_incomplete_tracks(1)
    if not incomplete_tracks_response['success']:
        return jsonify(
            {"error": f"Error in update_tracks (get_incomplete_tracks): {incomplete_tracks_response['error']}"}), 500

    incomplete_tracks = incomplete_tracks_response['data']
    for track in incomplete_tracks:
        track_id = track['tid']
        track_details_response = spotify_service.get_track_details(access_token, track_id)
        if not track_details_response['success']:
            if track_details_response['error'] == '404':
                logging.warning(f"Track not found: {track_id}")
                continue
            return jsonify(
                {"error": f"Error in update_tracks (get_track_details): {track_details_response['error']}"}), 500

        track_data = track_details_response['data']
        update_track_response = db_service.update_track(
            track_id, track_data['danceability'], track_data['energy'], track_data['key'],
            track_data['loudness'], track_data['mode'], track_data['speechiness'],
            track_data['acousticness'], track_data['instrumentalness'], track_data['liveness'],
            track_data['valence'], track_data['tempo']
        )
        if not update_track_response['success']:
            return jsonify({"error": f"Error in update_tracks (update_track): {update_track_response['error']}"}), 500

    return jsonify({"message": "Tracks updated successfully"}), 200
