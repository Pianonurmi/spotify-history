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

# Spotify Fetcher Deployment

This guide explains how to deploy the Spotify Fetcher service using Docker and Docker Compose. The setup uses a prebuilt Docker image hosted on Docker Hub.

---

## Prerequisites

1. Install Docker and Docker Compose:
   - [Docker Installation Guide](https://docs.docker.com/get-docker/)
   - [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)
2. Clone this repository:
   ```bash
   git clone https://github.com/Pianonurmi/spotify-history/docker-compose.git
   cd docker-compose
Create a .env file in the home-repo directory to store environment variables. Example:
env
Kopioi koodi
POSTGRES_USER=your_postgres_username
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=spotify_db
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
Steps to Deploy
1. Set Up the Environment
Ensure the .env file is properly configured with your values. These variables are used for both the PostgreSQL database and the Spotify Fetcher service.

2. Start the Services
Run the following command to deploy the services using Docker Compose:

bash
Kopioi koodi
docker-compose up -d
3. Verify the Deployment
PostgreSQL:
Accessible on port 5432 on localhost.
Credentials: Use the values from your .env file.
Spotify Fetcher:
Accessible on port 8888 on localhost.
Logs can be viewed with:
bash
Kopioi koodi
docker logs spotify_fetcher
Folder Structure
graphql
Kopioi koodi
docker-compose/
├── docker-compose.yml       # Docker Compose file for service configuration
├── data/                    # Directory for PostgreSQL data persistence
├── init/                    # Directory for PostgreSQL initialization scripts
│   └── init.sql             # Initial database schema setup
├── fetcher/                 # Directory for storing Spotify tokens
└── .env                     # Environment variables for configuration
Notes
If you encounter any issues, check the logs for more details:
bash
Kopioi koodi
docker-compose logs
Make sure the SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI values match your Spotify Developer Application settings.
Stopping the Services
To stop and remove all containers:

bash
Kopioi koodi
docker-compose down
Clean-Up
To remove all volumes and data:

bash
Kopioi koodi
docker-compose down --volumes
Contributions
Feel free to fork this repository and submit pull requests to improve the service.

License
This project is licensed under MIT License.

vbnet
Kopioi koodi

This `README.md` provides clear instructions for deployment and troubleshooting, tailored for GitHub. 
