CREATE TABLE IF NOT EXISTS spotify_history (
    id SERIAL PRIMARY KEY,               -- Unique ID for each record
    track_id VARCHAR(50) NOT NULL,       -- Spotify track ID
    track_name TEXT,                     -- Name of the track
    artist_name TEXT,                    -- Artist(s) name
    played_at TIMESTAMP NOT NULL,        -- Time when the track was played
    CONSTRAINT unique_track_play UNIQUE (track_id, played_at) -- Ensure no duplicate play records for the same track at the same time
);
