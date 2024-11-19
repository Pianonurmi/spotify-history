import os
import time
import json
import requests
import psycopg2
from flask import Flask, request
import logging  # Added for logging

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO for less verbosity in production
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Application started.")  # Log to confirm logging is working

# Environment Variables
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")

# Directory and file path
TOKENS_DIR = "/app/spotify_tokens"
TOKENS_FILE = os.path.join(TOKENS_DIR, "spotify_tokens.json")

# Initialize Flask for authentication
app = Flask(__name__)

# Ensure the directory exists
if not os.path.exists(TOKENS_DIR):
    os.makedirs(TOKENS_DIR)
    logging.info(f"Created tokens directory at {TOKENS_DIR}")

@app.route("/callback")
def spotify_callback():
    code = request.args.get("code")
    logging.debug(f"Received code: {code}")
    
    try:
        token_response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        token_response.raise_for_status()  # Raise an error for HTTP issues
        tokens = token_response.json()
        with open(TOKENS_FILE, "w") as file:
            json.dump(tokens, file)
        logging.info("Tokens saved successfully.")
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve tokens: {e}")
        return "Error during token retrieval."
    
    shutdown_server()
    return "Authentication successful. You can close this window."

def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func:
        logging.info("Shutting down the Flask server.")
        func()

def authenticate():
    logging.info("Starting Spotify authentication process.")
    logging.info("Go to the following URL to authenticate:")
    logging.info(
        f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=user-read-recently-played"
    )
    app.run(host="0.0.0.0", port=8888)

def refresh_token():
    logging.info("Refreshing Spotify access token.")
    try:
        with open(TOKENS_FILE, "r") as file:
            tokens = json.load(file)
        refresh_response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": tokens["refresh_token"],
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        refresh_response.raise_for_status()
        new_tokens = refresh_response.json()
        tokens.update(new_tokens)
        with open(TOKENS_FILE, "w") as file:
            json.dump(tokens, file)
        logging.info("Token refresh successful.")
        return tokens["access_token"]
    except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
        logging.error(f"Error refreshing token: {e}")
        raise

def fetch_recently_played():
    logging.info("Fetching recently played tracks from Spotify.")
    try:
        token = refresh_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50", headers=headers)
        response.raise_for_status()
        logging.info("Fetched recently played tracks successfully.")
        return response.json().get("items", [])
    except requests.RequestException as e:
        logging.error(f"Error fetching recently played tracks: {e}")
        return []

def save_to_db(data):
    max_retries = 10  # Set a limit for retries to avoid infinite loops
    retry_delay = 5   # Delay in seconds between retries

    logging.info("Attempting to connect to the database.")
    connection = None
    for attempt in range(max_retries):
        try:
            connection = psycopg2.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME
            )
            logging.info("Database connection successful.")
            break
        except psycopg2.OperationalError as e:
            logging.warning(f"Database connection failed: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    else:
        logging.error("Failed to connect to the database after several retries. Exiting...")
        return
    
    cursor = connection.cursor()
    for item in data:
        track = item["track"]
        played_at = item["played_at"]
        track_id = track["id"]
        track_name = track["name"]
        artist_name = track["artists"][0]["name"]
        
        logging.debug(f"Processing track: {track_name} by {artist_name}, played at {played_at}")
        
        # Check if the track already exists in the database
        cursor.execute(
            "SELECT 1 FROM spotify_history WHERE track_id = %s", (track_id,)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO spotify_history (track_id, track_name, artist_name, played_at) VALUES (%s, %s, %s, %s)",
                (track_id, track_name, artist_name, played_at),
            )
            connection.commit()
            logging.info(f"Inserted track: {track_name} by {artist_name}")
    connection.close()

if __name__ == "__main__":
    if not os.path.exists(TOKENS_FILE):
        logging.info("No tokens file found. Starting authentication.")
        authenticate()
    while True:
        logging.info("Fetching and saving recently played tracks.")
        data = fetch_recently_played()
        save_to_db(data)
        logging.info("Sleeping for 10 minutes before the next fetch.")
        time.sleep(600)  # Fetch every 10 minutes
