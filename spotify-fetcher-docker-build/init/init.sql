CREATE TABLE IF NOT EXISTS spotify_history (
    id SERIAL PRIMARY KEY,
    track_id VARCHAR(50) UNIQUE,
    track_name TEXT,
    artist_name TEXT,
    played_at TIMESTAMP
);
