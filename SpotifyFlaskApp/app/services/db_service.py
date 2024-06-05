import logging
from sqlalchemy import text
from datetime import datetime, timedelta
from app.helpers.db_helper import get_db_session


class DBService:
    def __init__(self):
        self.db = next(get_db_session())

    def __del__(self):
        self.db.close()

    def insert_user(self, spotify_uuid, name, active, spotify_key):
        try:
            count_user = self.db.execute(
                text("SELECT COUNT(*) FROM users WHERE spotify_uuid = :spotify_uuid"),
                {'spotify_uuid': spotify_uuid}
            ).scalar()

            if count_user == 0:
                self.db.execute(
                    text(
                        "INSERT INTO users (spotify_uuid, name, active, spotify_key) VALUES (:spotify_uuid, :name, :active, :spotify_key)"
                    ),
                    {'spotify_uuid': spotify_uuid, 'name': name, 'active': active, 'spotify_key': spotify_key}
                )
            else:
                self.db.execute(
                    text("UPDATE users SET spotify_key = :spotify_key WHERE spotify_uuid = :spotify_uuid"),
                    {'spotify_key': spotify_key, 'spotify_uuid': spotify_uuid}
                )

            self.db.commit()
            logging.info(f"User inserted/updated successfully - {name}")
            return {'success': True, 'message': 'User inserted/updated successfully'}
        except Exception as e:
            self.db.rollback()
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
            return {'success': False, 'error': f"Error occurred in get_active_users while getting active users: {e}"}

    def insert_artist(self, artist):
        try:
            self.db.execute(
                text("INSERT INTO artists (aid, name) VALUES (:aid, :name)"),
                {'aid': artist['id'], 'name': artist['name']}
            )
            self.db.commit()
            logging.info(f"Artist inserted successfully - {artist['name']}")
            return {'success': True, 'message': 'Artist inserted successfully'}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': f"Error occurred in insert_artist while inserting artist: {e}"}

    def insert_track(self, track):
        try:
            artist = track['artists'][0]
            count_artist = self.db.execute(
                text("SELECT COUNT(*) FROM artists WHERE aid = :aid"),
                {'aid': artist['id']}
            ).scalar()

            if count_artist == 0:
                success_or_error = self.insert_artist(artist)
                if not success_or_error['success']:
                    return success_or_error

            self.db.execute(
                text("INSERT INTO tracks (tid, name, artist, image) VALUES (:tid, :name, :artist, :image)"),
                {'tid': track['id'], 'name': track['name'], 'artist': artist['id'],
                 'image': track['album']['images'][0]['url']}
            )
            self.db.commit()
            logging.info(f"Track inserted successfully - {track['name']}")
            return {'success': True, 'message': 'Track inserted successfully'}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': f"Error occurred in insert_track while inserting track: {e}"}

    def insert_track_into_recent(self, played_at, spotify_uuid, track):
        try:
            count_track = self.db.execute(
                text("SELECT COUNT(*) FROM tracks WHERE tid = :tid"),
                {'tid': track['id']}
            ).scalar()

            if count_track == 0:
                success_or_error = self.insert_track(track)
                if not success_or_error['success']:
                    return success_or_error

            self.db.execute(
                text("INSERT INTO recent (played_at, uid, tid) VALUES (:played_at, :uid, :tid)"),
                {'played_at': played_at, 'uid': spotify_uuid, 'tid': track['id']}
            )
            self.db.commit()
            logging.info(f"Recent inserted successfully - {track['name']} - for User: {spotify_uuid}")
            return {'success': True,
                    'message': f"Recent inserted successfully - {track['name']} - for User: {spotify_uuid}"}
        except Exception as e:
            self.db.rollback()
            if "duplicate key value violates unique constraint" in str(e):
                logging.info(f"Recent already in database - {track['name']} - for User: {spotify_uuid}")
                return {'success': True,
                        'message': f"Recent already in database - {track['name']} - for User: {spotify_uuid}"}
            return {'success': False,
                    'error': f"Error occurred in insert_track_into_recent while inserting recent track: {e}"}

    def insert_genre(self, genre):
        try:
            result = self.db.execute(
                text("INSERT INTO genres (name) VALUES (:name) ON CONFLICT (name) DO NOTHING RETURNING gid"),
                {'name': genre}
            )
            genre_record = result.fetchone()
            self.db.commit()

            if genre_record is None:
                result = self.db.execute(
                    text("SELECT gid FROM genres WHERE name = :name"),
                    {'name': genre}
                )
                genre_record = result.fetchone()
            logging.info(f"Genre inserted successfully - {genre}")
            return {'success': True, 'message': 'Genre inserted successfully', 'data': genre_record[0]}
        except Exception as e:
            self.db.rollback()
            if "duplicate key value violates unique constraint" in str(e):
                logging.info(f"Genre already in database - {genre}")
                return {'success': True, 'message': 'Genre already in database'}
            return {'success': False, 'error': f"Error occurred in insert_genre while inserting genre: {e}"}

    def get_listened_to(self, start_date=None, end_date=None, spotify_uuid=None, limit=50000):
        try:
            if start_date is None:
                # Default to last 14 days
                start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
            if end_date is None:
                # Default to today
                end_date = datetime.now().strftime('%Y-%m-%d')

            query = """
            SELECT * FROM recent
            WHERE uid = :uid AND played_at BETWEEN :start_date AND :end_date
            """
            params = {'uid': spotify_uuid, 'start_date': start_date, 'end_date': end_date}
            if limit > 0:
                query += " LIMIT :limit"
                params['limit'] = limit

            result = self.db.execute(text(query), params)
            listened_to = [dict(row) for row in result.mappings()]

            if not listened_to:
                return {'success': False, 'error': 'No songs found'}
            logging.info(f"Songs retrieved successfully - {len(listened_to)}")
            return {'success': True, 'message': 'Songs retrieved successfully', 'data': listened_to}
        except Exception as e:
            return {'success': False, 'error': f"Error occurred in get_listened_to while getting songs: {e}"}

    def get_incomplete_artists(self):
        try:
            result = self.db.execute(
                text("SELECT aid FROM artists WHERE complete = FALSE")
            )
            incomplete_artists = [dict(row) for row in result.mappings()]
            logging.info(f"Incomplete artists retrieved successfully - {len(incomplete_artists)}")
            return {'success': True, 'message': 'Incomplete artists retrieved successfully', 'data': incomplete_artists}
        except Exception as e:
            return {'success': False,
                    'error': f"Error occurred in get_incomplete_artists while getting incomplete artists: {e}"}

    def update_artist(self, artist_id, genres, image):
        if genres is None:
            genres = []
        try:
            self.db.execute(
                text("UPDATE artists SET image = :image, complete = TRUE WHERE aid = :aid"),
                {'image': image, 'aid': artist_id}
            )

            for genre in genres:
                result = self.db.execute(
                    text("INSERT INTO genres (name) VALUES (:name) ON CONFLICT (name) DO NOTHING RETURNING gid"),
                    {'name': genre}
                )
                genre_record = result.fetchone()
                if genre_record is None:
                    result = self.db.execute(
                        text("SELECT gid FROM genres WHERE name = :name"),
                        {'name': genre}
                    )
                    genre_record = result.fetchone()

                genre_id = genre_record[0]
                self.db.execute(
                    text("INSERT INTO artist_genre (aid, gid) VALUES (:aid, :gid) ON CONFLICT DO NOTHING"),
                    {'aid': artist_id, 'gid': genre_id}
                )

            self.db.commit()
            logging.info(f"Artist updated successfully - {artist_id}")
            return {'success': True, 'message': 'Artist updated successfully'}
        except Exception as e:
            self.db.rollback()
            if "duplicate key value violates unique constraint" in str(e):
                return {'success': True, 'message': 'Artist already in database'}
            return {'success': False, 'error': f"Error occurred in update_artist while updating artist: {e}"}
