# app/routes/playlist.py
from flask import Blueprint, jsonify, request

from app.routes.route_helper import get_tokens_from_headers
from app.services import SpotifyService, DBService

# Define the Blueprint
bp = Blueprint('playlist', __name__)

# Initialize services
spotify_service = SpotifyService()
db_service = DBService()


@bp.route('/', methods=['GET'])
def pp():
    refresh_token, spotify_uuid = get_tokens_from_headers()
    if not refresh_token or not spotify_uuid:
        return jsonify({"message": "Missing required headers)"}), 400
    # Get user info from DB
    return jsonify({"message": "BOILERPLATE TO GET PLAYLISTS"}), 200