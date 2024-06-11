import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import atexit

from app import Config
from app.services.db_service import DBService  # Correct the import statement


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=hourly_task, trigger="interval", hours=1)  # Pass the function without calling it
    scheduler.add_job(func=daily_task, trigger="cron", hour=0, minute=0)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    logging.info("Scheduler started with minute and daily tasks.")


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
                'Authorization': refresh_token,
                'Spotify-UUID': spotify_uuid
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
