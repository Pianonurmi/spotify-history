# Spotify Fetcher and Database Logger

This project fetches your recently played Spotify tracks and stores them in a PostgreSQL database for analysis and tracking.

## Features

- **Authentication**: Uses Spotify's OAuth2.0 to authenticate the user and obtain access tokens.
- **Token Refresh**: Automatically refreshes the access token once it expires using the refresh token.
- **Fetch Recently Played Tracks**: Pulls the last 50 tracks played from Spotify.
- **Database Storage**: Saves the fetched track data in a PostgreSQL database.

## How It Works

1. **Initial Token Retrieval**:
   - When the user first authenticates, a set of access and refresh tokens is saved to the file `spotify_tokens.json` in the `/app/spotify_tokens` directory. This is done in the `spotify_callback()` function, which is called after the user authorizes the application through Spotify.

2. **Refreshing the Token**:
   - The `refresh_token()` function checks for the `refresh_token` inside the `spotify_tokens.json` file. If the `refresh_token` is available, it sends a request to Spotify’s API (`/api/token`) to get a new access token using the refresh token.
   - If the refresh is successful, it updates the tokens in the `spotify_tokens.json` file.

   **refresh_token() function:**
   ```python
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
3. **Recently Played Tracks:**

The function fetch_recently_played() calls refresh_token() to ensure the app always has a valid access token before attempting to fetch the data from Spotify. If the access token has expired, it will be refreshed automatically before making the request.
fetch_recently_played() function:

python
Kopioi koodi
def fetch_recently_played():
    logging.info("Fetching recently played tracks from Spotify.")
    try:
        token = refresh_token()  # Ensures fresh token is used
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50", headers=headers)
        response.raise_for_status()
        logging.info("Fetched recently played tracks successfully.")
        return response.json().get("items", [])
    except requests.RequestException as e:
        logging.error(f"Error fetching recently played tracks: {e}")
        return []
