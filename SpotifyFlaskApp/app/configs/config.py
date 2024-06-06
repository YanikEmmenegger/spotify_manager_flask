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


# Call this method to print the configuration for debugging
# Config.print_config()
