import logging
from datetime import datetime
from sqlalchemy import text
from app.helpers.db_helper import get_db_session


class DBService:
    def __init__(self):
        self.db = next(get_db_session())

    def __del__(self):
        self.db.close()

    def insert_user(self, spotify_uuid, name, active, spotify_key):
        try:
            user_exists = self.db.execute(
                text("SELECT 1 FROM users WHERE spotify_uuid = :spotify_uuid"),
                {'spotify_uuid': spotify_uuid}
            ).scalar()

            if user_exists:
                self.db.execute(
                    text("UPDATE users SET spotify_key = :spotify_key WHERE spotify_uuid = :spotify_uuid"),
                    {'spotify_key': spotify_key, 'spotify_uuid': spotify_uuid}
                )
                logging.info(f"User updated successfully - {name}")
            else:
                self.db.execute(
                    text(
                        "INSERT INTO users (spotify_uuid, name, active, spotify_key) VALUES (:spotify_uuid, :name, :active, :spotify_key)"),
                    {'spotify_uuid': spotify_uuid, 'name': name, 'active': active, 'spotify_key': spotify_key}
                )
                logging.info(f"User inserted successfully - {name}")

            self.db.commit()
            return {'success': True, 'message': 'User inserted/updated successfully'}
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error in insert_user: {e}")
            return {'success': False, 'error': f"Error occurred in insert_user while inserting/updating user: {e}"}

    def get_active_users(self, limit=100000):
        try:
            result = self.db.execute(
                text("SELECT spotify_uuid, name, active, spotify_key FROM users WHERE active = TRUE LIMIT :limit"),
                {'limit': limit}
            )
            active_users = [dict(row) for row in result.mappings()]

            if not active_users:
                return {'success': False, 'error': 'No active users found'}
            logging.info(f"Active users retrieved successfully - {len(active_users)}")
            return {'success': True, 'message': 'Active users retrieved successfully', 'data': active_users}
        except Exception as e:
            logging.error(f"Error in get_active_users: {e}")
            return {'success': False, 'error': f"Error occurred in get_active_users while getting active users: {e}"}

    def get_user_by_token(self, token):
        try:
            result = self.db.execute(
                text("SELECT * FROM users WHERE spotify_key = :token"),
                {'token': token}
            )
            user = [dict(row) for row in result.mappings()]

            if not user:
                return {'success': False, 'error': 'No user found'}
            logging.info(f"User retrieved successfully - {user[0]['name']}")
            return {'success': True, 'message': 'User retrieved successfully', 'data': user[0]}
        except Exception as e:
            logging.error(f"Error in get_user_by_token: {e}")
            return {'success': False, 'error': f"Error occurred in get_user_by_token while getting user: {e}"}

    def insert_artist(self, artist):
        try:
            artist_exists = self.db.execute(
                text("SELECT 1 FROM artists WHERE aid = :aid"),
                {'aid': artist['id']}
            ).scalar()

            if not artist_exists:
                self.db.execute(
                    text("INSERT INTO artists (aid, name) VALUES (:aid, :name) ON CONFLICT (aid) DO NOTHING"),
                    {'aid': artist['id'], 'name': artist['name']}
                )
                self.db.commit()
                logging.info(f"Artist inserted successfully - {artist['name']}")
            else:
                logging.info(f"Artist already exists - {artist['name']}")
            return {'success': True, 'message': 'Artist inserted/updated successfully'}
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error in insert_artist: {e}")
            return {'success': False, 'error': f"Error occurred in insert_artist while inserting artist: {e}"}

    def insert_track(self, track):
        try:
            track_exists = self.db.execute(
                text("SELECT 1 FROM tracks WHERE tid = :tid"),
                {'tid': track['id']}
            ).scalar()

            if not track_exists:
                artist = track['artists'][0]
                self.insert_artist(artist)
                self.db.execute(
                    text(
                        "INSERT INTO tracks (tid, name, artist, image) VALUES (:tid, :name, :artist, :image) ON CONFLICT (tid) DO NOTHING"),
                    {'tid': track['id'], 'name': track['name'], 'artist': artist['id'],
                     'image': track['album']['images'][0]['url']}
                )
                self.db.commit()
                logging.info(f"Track inserted successfully - {track['name']}")
            else:
                logging.info(f"Track already exists - {track['name']}")
            return {'success': True, 'message': 'Track inserted/updated successfully'}
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error in insert_track: {e}")
            return {'success': False, 'error': f"Error occurred in insert_track while inserting track: {e}"}

    def insert_track_into_recent(self, played_at, spotify_uuid, track):
        try:
            track_exists = self.db.execute(
                text("SELECT 1 FROM tracks WHERE tid = :tid"),
                {'tid': track['id']}
            ).scalar()

            if not track_exists:
                self.insert_track(track)

            self.db.execute(
                text(
                    "INSERT INTO recent (played_at, uid, tid) VALUES (:played_at, :uid, :tid) ON CONFLICT (played_at, uid, tid) DO NOTHING"),
                {'played_at': played_at, 'uid': spotify_uuid, 'tid': track['id']}
            )
            self.db.commit()
            logging.info(f"Recent inserted successfully - {track['name']} - for User: {spotify_uuid}")
            return {'success': True,
                    'message': f"Recent inserted successfully - {track['name']} - for User: {spotify_uuid}"}
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error in insert_track_into_recent: {e}")
            return {'success': False,
                    'error': f"Error occurred in insert_track_into_recent while inserting recent track: {e}"}

    def delete_topmix_exception(self, spotify_uuid, value):
        try:
            self.db.execute(
                text("DELETE FROM topmix_exception WHERE spotify_uuid = :spotify_uuid AND value = :value"),
                {'spotify_uuid': spotify_uuid, 'value': value}
            )
            self.db.commit()
            logging.info(f"Exception deleted successfully - {value}")
            return {'success': True, 'message': 'Exception deleted successfully'}
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error in delete_topmix_exception: {e}")
            return {'success': False,
                    'error': f"Error occurred in delete_topmix_exception while deleting exception: {e}"}

    def insert_topmix_exception(self, spotify_uuid, exception_type, value):
        if exception_type not in ['artist', 'track']:
            return {'success': False, 'error': 'Invalid exception type. Must be "artist" or "track"'}

        try:
            self.db.execute(
                text(
                    "INSERT INTO topmix_exception (spotify_uuid, type, value) VALUES (:spotify_uuid, :type, :value) ON CONFLICT DO NOTHING"),
                {'spotify_uuid': spotify_uuid, 'type': exception_type, 'value': value}
            )
            self.db.commit()
            logging.info(f"Exception inserted successfully - {exception_type} - {value}")
            return {'success': True, 'message': 'Exception inserted successfully'}
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error in insert_topmix_exception: {e}")
            return {'success': False,
                    'error': f"Error occurred in insert_topmix_exception while inserting exception: {e}"}

    def insert_genre(self, genre):
        try:
            genre_exists = self.db.execute(
                text("SELECT 1 FROM genres WHERE name = :name"),
                {'name': genre}
            ).scalar()

            if not genre_exists:
                result = self.db.execute(
                    text("INSERT INTO genres (name) VALUES (:name) ON CONFLICT (name) DO NOTHING RETURNING gid"),
                    {'name': genre}
                )
                genre_record = result.fetchone()
                self.db.commit()

                if not genre_record:
                    genre_record = self.db.execute(
                        text("SELECT gid FROM genres WHERE name = :name"),
                        {'name': genre}
                    ).fetchone()
                logging.info(f"Genre inserted successfully - {genre}")
                return {'success': True, 'message': 'Genre inserted successfully', 'data': genre_record[0]}
            else:
                genre_record = self.db.execute(
                    text("SELECT gid FROM genres WHERE name = :name"),
                    {'name': genre}
                ).fetchone()
                logging.info(f"Genre already exists - {genre}")
                return {'success': True, 'message': 'Genre already exists', 'data': genre_record[0]}
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error in insert_genre: {e}")
            return {'success': False, 'error': f"Error occurred in insert_genre while inserting genre: {e}"}

    def get_listened_to(self, start_date=None, end_date=None, spotify_uuid=None, limit=200, offset=0,
                        artist_exceptions=None,
                        track_exceptions=None, extended=False):
        try:
            query = """
            SELECT recent.*, tracks.name AS track_name, tracks.image AS track_image, tracks.*{artist_fields} FROM recent
            JOIN tracks ON recent.tid = tracks.tid
            {join_artists}
            WHERE recent.uid = :uid
            {date_condition}
            {artist_exceptions_condition}
            {track_exceptions_condition}
            ORDER BY recent.played_at DESC
            LIMIT :limit OFFSET :offset
            """

            count_query = """
            SELECT COUNT(*) FROM recent
            JOIN tracks ON recent.tid = tracks.tid
            {join_artists}
            WHERE recent.uid = :uid
            {date_condition}
            {artist_exceptions_condition}
            {track_exceptions_condition}
            """

            params = {'uid': spotify_uuid, 'limit': limit, 'offset': offset}

            if start_date and end_date:
                date_condition = "AND recent.played_at BETWEEN :start_date AND :end_date"
                params.update({'start_date': start_date, 'end_date': end_date})
            else:
                date_condition = ""

            if artist_exceptions:
                artist_exceptions_condition = "AND tracks.artist NOT IN :artist_exceptions"
                params['artist_exceptions'] = tuple(artist_exceptions)
            else:
                artist_exceptions_condition = ""

            if track_exceptions:
                track_exceptions_condition = "AND recent.tid NOT IN :track_exceptions"
                params['track_exceptions'] = tuple(track_exceptions)
            else:
                track_exceptions_condition = ""

            if extended:
                artist_fields = ", artists.*"
                join_artists = "JOIN artists ON tracks.artist = artists.aid"
            else:
                artist_fields = ""
                join_artists = ""

            query = query.format(
                artist_fields=artist_fields,
                join_artists=join_artists,
                date_condition=date_condition,
                artist_exceptions_condition=artist_exceptions_condition,
                track_exceptions_condition=track_exceptions_condition
            )

            count_query = count_query.format(
                join_artists=join_artists,
                date_condition=date_condition,
                artist_exceptions_condition=artist_exceptions_condition,
                track_exceptions_condition=track_exceptions_condition
            )

            result = self.db.execute(text(query), params)
            listened_to = [dict(row) for row in result.mappings()]

            # Get total count of results ignoring limit and offset
            count_result = self.db.execute(text(count_query), params)
            total_count = count_result.scalar()

            # Convert datetime objects to strings
            for item in listened_to:
                if isinstance(item['played_at'], datetime):
                    item['played_at'] = item['played_at'].isoformat()

            if not listened_to:
                return {'success': False, 'error': 'No songs found'}

            logging.info(f"Songs retrieved successfully - {len(listened_to)}")
            return {'success': True, 'message': 'Songs retrieved successfully', 'data': listened_to,
                    'total_count': total_count}

        except Exception as e:
            logging.error(f"Error in get_listened_to: {e}")
            return {'success': False, 'error': f"Error occurred in get_listened_to while getting songs: {e}"}

    def get_incomplete_artists(self, limit=1000):
        try:
            result = self.db.execute(
                text("SELECT aid FROM artists WHERE complete = FALSE LIMIT :limit"),
                {'limit': limit}
            )
            incomplete_artists = [dict(row) for row in result.mappings()]
            logging.info(f"Incomplete artists retrieved successfully - {len(incomplete_artists)}")
            return {'success': True, 'message': 'Incomplete artists retrieved successfully', 'data': incomplete_artists}
        except Exception as e:
            logging.error(f"Error in get_incomplete_artists: {e}")
            return {'success': False,
                    'error': f"Error occurred in get_incomplete_artists while getting incomplete artists: {e}"}

    def get_topmix_exceptions(self, spotify_uuid):
        try:
            result = self.db.execute(
                text("SELECT * FROM topmix_exception WHERE spotify_uuid = :uid"),
                {'uid': spotify_uuid}
            )
            exceptions = [dict(row) for row in result.mappings()]

            artist_exceptions = [exception['value'] for exception in exceptions if exception['type'] == 'artist']
            track_exceptions = [exception['value'] for exception in exceptions if exception['type'] == 'track']
            exceptions = {'artists': artist_exceptions, 'tracks': track_exceptions}

            logging.info(f"Exceptions retrieved successfully - {len(exceptions)}")
            return {'success': True, 'message': 'Exceptions retrieved successfully', 'data': exceptions}
        except Exception as e:
            logging.error(f"Error in get_topmix_exceptions: {e}")
            return {'success': False, 'error': f"Error occurred in get_topmix_exceptions while getting exceptions: {e}"}

    def update_artist(self, artist_id, genres, image):
        if genres is None:
            genres = []
        try:
            self.db.execute(
                text("UPDATE artists SET image = :image, complete = TRUE WHERE aid = :aid"),
                {'image': image, 'aid': artist_id}
            )

            for genre in genres:
                genre_record = self.db.execute(
                    text("INSERT INTO genres (name) VALUES (:name) ON CONFLICT (name) DO NOTHING RETURNING gid"),
                    {'name': genre}
                ).fetchone()

                if not genre_record:
                    genre_record = self.db.execute(
                        text("SELECT gid FROM genres WHERE name = :name"),
                        {'name': genre}
                    ).fetchone()

                self.db.execute(
                    text("INSERT INTO artist_genre (aid, gid) VALUES (:aid, :gid) ON CONFLICT DO NOTHING"),
                    {'aid': artist_id, 'gid': genre_record[0]}
                )

            self.db.commit()
            logging.info(f"Artist updated successfully - {artist_id}")
            return {'success': True, 'message': 'Artist updated successfully'}
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error in update_artist: {e}")
            return {'success': False, 'error': f"Error occurred in update_artist while updating artist: {e}"}

    def get_incomplete_tracks(self, limit=1000):
        try:
            result = self.db.execute(
                text("SELECT tid FROM tracks where complete = FALSE LIMIT :limit"),
                {'limit': limit}
            )
            incomplete_tracks = [dict(row) for row in result.mappings()]
            logging.info(f"Incomplete tracks retrieved successfully - {len(incomplete_tracks)}")
            return {'success': True, 'message': 'Incomplete tracks retrieved successfully', 'data': incomplete_tracks}
        except Exception as e:
            logging.error(f"Error in get_incomplete_tracks: {e}")
            return {'success': False,
                    'error': f"Error occurred in get_incomplete_tracks while getting incomplete tracks: {e}"}

    def update_track(self, track_id, danceability, energy, key, loudness, mode, speechiness, acousticness,
                     instrumentalness, liveness, valence, tempo):
        try:
            self.db.execute(
                text(
                    "UPDATE tracks SET danceability = :danceability, energy = :energy, key = :key, loudness = :loudness, mode = :mode, speechiness = :speechiness, acousticness = :acousticness, instrumentalness = :instrumentalness, liveness = :liveness, valence = :valence, tempo = :tempo, complete = TRUE WHERE tid = :tid"),
                {
                    'danceability': danceability, 'energy': energy, 'key': key, 'loudness': loudness, 'mode': mode,
                    'speechiness': speechiness, 'acousticness': acousticness, 'instrumentalness': instrumentalness,
                    'liveness': liveness, 'valence': valence, 'tempo': tempo, 'tid': track_id
                }
            )
            self.db.commit()
            logging.info(f"Track updated successfully - {track_id}")
            return {'success': True, 'message': 'Track updated successfully'}
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error in update_track: {e}")
            return {'success': False, 'error': f"Error occurred in update_track while updating track: {e}"}
