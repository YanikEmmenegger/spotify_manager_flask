# app/routes/services.py
from flask import Blueprint, jsonify, request

from app.routes.route_helper import get_tokens_from_headers
from app.services import SpotifyService, DBService

# Define the Blueprint
bp = Blueprint('user', __name__)

# Initialize services
spotify_service = SpotifyService()
db_service = DBService()


@bp.route('/', methods=['GET'])
def get_user():
    refresh_token, spotify_uuid = get_tokens_from_headers()
    if not refresh_token or not spotify_uuid:
        return jsonify({"message": "Missing required headers)"}), 400
    # Get user info from DB
    return jsonify({"message": "BOILERPLATE TO GET USER INFOS"}), 200


@bp.route('/listened', methods=['GET'])
def get_listened_tracks():
    refresh_token, spotify_uuid = get_tokens_from_headers()
    if not refresh_token or not spotify_uuid:
        return jsonify({"message": "Missing required headers)"}), 400
    # get requests args
    limit = request.args.get('limit', 50)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    # Get listened tracks from DB
    listened_tracks_response = db_service.get_listened_to(start_date, end_date, spotify_uuid, limit,
                                                          None,
                                                          None, True)
    if not listened_tracks_response['success']:
        return jsonify({"error": f"Error in get_listened_tracks: {listened_tracks_response['error']}"}), 500

    listened_tracks = listened_tracks_response['data']
    response = {
        "status": "success",
        "count": len(listened_tracks),
        "data": listened_tracks
    }
    return jsonify(response), 200
