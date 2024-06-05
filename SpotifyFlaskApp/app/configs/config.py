import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
    SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
    SPOTIPY_SCOPES = os.getenv("SPOTIPY_SCOPES").split(',')

    POSTGRES_URL = os.getenv("POSTGRES_URL")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASS")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)

    @staticmethod
    def print_config():
        print(f"SPOTIPY_CLIENT_ID: {Config.SPOTIPY_CLIENT_ID}")
        print(f"SPOTIPY_CLIENT_SECRET: {Config.SPOTIPY_CLIENT_SECRET}")
        print(f"SPOTIPY_REDIRECT_URI: {Config.SPOTIPY_REDIRECT_URI}")
        print(f"SPOTIPY_SCOPES: {Config.SPOTIPY_SCOPES}")
        print(f"POSTGRESQL_URL: {Config.POSTGRES_URL}")
        print(f"POSTGRESQL_USER: {Config.POSTGRES_USER}")
        print(f"POSTGRESQL_PASS: {Config.POSTGRES_PASSWORD}")
        print(f"POSTGRESQL_DB: {Config.POSTGRES_DB}")
        print(f"POSTGRESQL_PORT: {Config.POSTGRES_PORT}")


# Call this method to print the configuration for debugging
# Config.print_config()
