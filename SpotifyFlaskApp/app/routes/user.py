import re

from flask import request
from flask_restful import Resource, url_for
from app.services import SpotifyService, DBService
from app.routes.route_helper import get_tokens_from_headers

spotify_service = SpotifyService()
db_service = DBService()


class GetUser(Resource):
    def get(self):
        try:
            refresh_token, spotify_uuid = get_tokens_from_headers()
            if not refresh_token or not spotify_uuid:
                return {"message": "Missing required headers"}, 400
            # Get user info from DB
            return {"message": "BOILERPLATE TO GET USER INFOS"}, 200
        except Exception as e:
            return {"error": f"Error in GetUser: {e}"}, 500


class GetListenedTracks(Resource):
    def get(self):
        try:
            refresh_token, spotify_uuid = get_tokens_from_headers()
            if not refresh_token or not spotify_uuid:
                return {"message": "Missing required headers"}, 400

            # Get all query parameters
            args = request.args

            # Validate and set limit and offset
            limit = args.get('limit', 200)
            offset = args.get('offset', 0)

            try:
                limit = int(limit)
                if limit < 1:
                    raise ValueError
            except ValueError:
                return {"error": "Limit must be a positive integer"}, 400

            try:
                offset = int(offset)
                if offset < 0:
                    raise ValueError
            except ValueError:
                return {"error": "Offset must be a non-negative integer"}, 400

            # Validate and set start_date and end_date
            start_date = args.get('start_date', None)  # must be YYYY-MM-DD ex. 2024-01-01
            end_date = args.get('end_date', None)  # must be YYYY-MM-DD ex. 2024-01-01

            date_regex = r'^\d{4}-\d{2}-\d{2}$'
            if start_date and not re.match(date_regex, start_date):
                return {"error": "start_date must be in format YYYY-MM-DD"}, 400
            if end_date and not re.match(date_regex, end_date):
                return {"error": "end_date must be in format YYYY-MM-DD"}, 400

            listened_tracks_response = db_service.get_listened_to(start_date, end_date, spotify_uuid, limit, offset,
                                                                  None, None, True)
            if not listened_tracks_response['success']:
                return {"error": f"Error in get_listened_tracks: {listened_tracks_response['error']}"}, 500

            listened_tracks = listened_tracks_response['data']
            total_count = listened_tracks_response.get('total_count', 0)

            response = {
                "status": "success",
                "count": len(listened_tracks),
                "total_count": total_count,
                "data": listened_tracks
            }

            # Add next link if there are more results
            if offset + limit < total_count:
                next_offset = offset + limit
                next_link = url_for('getlistenedtracks', limit=limit, offset=next_offset, start_date=start_date,
                                    end_date=end_date, _external=True)
                response["next"] = next_link

            return response, 200

        except Exception as e:
            return {"error": f"Error in GetListenedTracks: {e}"}, 500
