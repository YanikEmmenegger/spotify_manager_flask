# Spotify Manager Flask App

This project is a Flask application designed to interact with the Spotify API. It allows users to save their recently played tracks and update a Topmix playlist. The application uses PostgreSQL as the database and is structured to follow best practices in Python and Flask.

## Features

- Save recently played Spotify tracks to the database
- Update a Topmix playlist with the most played tracks over a specified period
- API endpoints to trigger these actions

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Docker
- Docker Compose

## Getting Started

### Create a Spotify Developer Account
a
To use this application, you'll need to create a Spotify Developer account and set up a new application to get the necessary credentials.

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
2. Log in with your Spotify account.
3. Click on **Create an App**.
4. Fill in the required details and click **Create**.
5. You will be provided with a **Client ID** and **Client Secret**.

### Configure Environment Variables

Create a `.env` file in the `SpotifyFlaskApp` directory with the following content:

```plaintext
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:5000/callback
SPOTIPY_SCOPES=ugc-image-upload,user-read-recently-played,user-top-read,user-read-playback-position,user-read-playback-state,user-modify-playback-state,user-read-currently-playing,app-remote-control,streaming,playlist-modify-public,playlist-modify-private,playlist-read-private,playlist-read-collaborative,user-library-modify,user-library-read,user-read-email,user-read-private

POSTGRESQL_URL=your_postgresql_url
POSTGRESQL_USER=your_postgresql_user
POSTGRESQL_PASS=your_postgresql_password
POSTGRESQL_DB=your_postgresql_db
POSTGRESQL_PORT=your_postgresql_port
