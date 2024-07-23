import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import atexit

from app import Config
from app.services import SpotifyService
from app.services.db_service import DBService

db_service = DBService()  # Initialize the DBService

# Correct the import statement
spotify_service = SpotifyService()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=hourly_task, trigger="interval", minutes=1)  # Pass the function without calling it
    scheduler.add_job(func=daily_task, trigger="cron", hour=0, minute=0)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    logging.info("Scheduler started with hourly and daily tasks.")


def update_tracks_task():
    logging.info("Spotify Update Tracks Task ...")
    try:
        get_incomplete_tracks_response = db_service.get_incomplete_tracks(10000)
        if not get_incomplete_tracks_response['success']:
            logging.error(
                f"Error in update_tracks_task (get_incomplete_tracks): {get_incomplete_tracks_response['error']}")
            return get_incomplete_tracks_response['error']

        get_first_active_user_response = db_service.get_active_users(1)
        if not get_first_active_user_response['success']:
            logging.error(
                f"Error in update_tracks_task (get_first_active_user): {get_first_active_user_response['error']}")
            return get_first_active_user_response['error']
        # print(get_first_active_user_response['data'])

        access_token = spotify_service.exchange_refresh_token(get_first_active_user_response['data'][0]['spotify_key'])
        if not access_token['success']:
            logging.error(f"Error in update_tracks_task (exchange_refresh_token): {access_token['error']}")
            return access_token['error']

        for track in get_incomplete_tracks_response['data']:

            print(track)
            get_track_infos_response = spotify_service.get_track_details(access_token['access_token'], track['tid'])
            if not get_track_infos_response['success'] and get_track_infos_response['error'] != 'Failed: Not Found':
                # continue with next track
                logging.error(f"Error in update_tracks_task (get_track_infos): {get_track_infos_response['error']}")
                continue

            if get_track_infos_response['success']:
                track_infos = get_track_infos_response['data']
                print(track_infos)
                # Update the track in the database
                update_track_response = db_service.update_track(track['tid'],
                                                                track_infos['danceability'],
                                                                track_infos['energy'],
                                                                track_infos['key'],
                                                                track_infos['loudness'],
                                                                track_infos['mode'],
                                                                track_infos['speechiness'],
                                                                track_infos['acousticness'],
                                                                track_infos['instrumentalness'],
                                                                track_infos['liveness'],
                                                                track_infos['valence'],
                                                                track_infos['tempo'])
                if not update_track_response['success']:
                    logging.error(f"Error in update_tracks_task (update_track): {update_track_response['error']}")
                    continue
    except Exception as e:
        logging.error(f"Error  in update_tracks_task: {e}")
        return e


def hourly_task():
    logging.info("Spotify Saver Task ...")
    try:
        db_service = DBService()  # Initialize the DBService
        users_response = db_service.get_active_users()
        if not users_response['success']:
            logging.error(f"Error in hourly_task (get_all_users): {users_response['error']}")
            return users_response['error']

        users = users_response['data']
        for user in users:
            refresh_token = user['spotify_key']
            spotify_uuid = user['spotify_uuid']
            logging.info(f"Processing user: {spotify_uuid}")
            # Create HTTP request with headers Authorization: refresh_token and Spotify-UUID: spotify_uuid
            headers = {
                # Authorization Bearer
                'Authorization': f'Bearer ' + refresh_token,
            }

            print(headers)
            response = requests.post(Config.BASE_URL + "/api/service/save", headers=headers)
            if response.status_code != 200:
                logging.error(f"Error in hourly_task: {response.text}")
                continue
            response_data = response.json()
            logging.info(f"Response for user {spotify_uuid}: {response_data}")

    except Exception as e:
        logging.error(f"Error in hourly_task: {e}")
        return e


def daily_task():
    logging.info("Spotify Topmix Task ...")
    try:
        db_service = DBService()  # Initialize the DBService
        users_response = db_service.get_active_users()
        if not users_response['success']:
            logging.error(f"Error in daily_task (get_all_users): {users_response['error']}")
            return users_response['error']

        users = users_response['data']
        for user in users:
            refresh_token = user['spotify_key']
            spotify_uuid = user['spotify_uuid']
            logging.info(f"Processing user: {spotify_uuid}")
            # Create HTTP request with headers Authorization: refresh_token and Spotify-UUID: spotify_uuid
            headers = {
                'Authorization': refresh_token,
                'SpotifyUUID': spotify_uuid
            }

            print(headers)
            response = requests.post(Config.BASE_URL + "/api/service/topmix", headers=headers)
            if response.status_code != 200:
                logging.error(f"Error in daily_task: {response.text}")
                continue
            response_data = response.json()
            logging.info(f"Response for user {spotify_uuid}: {response_data}")

    except Exception as e:
        logging.error(f"Error in daily_task: {e}")
        return e
