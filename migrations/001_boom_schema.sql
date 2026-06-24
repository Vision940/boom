-- boom command rankings table to store all random booms
CREATE TABLE boom_command_rankings (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  command TEXT NOT NULL,
  ranking SMALLINT NOT NULL CHECK (ranking >= 1 AND ranking <= 6),
  multiplier SMALLINT NOT NULL DEFAULT 1,

  odds SMALLINT NOT NULL DEFAULT 15,
  drought SMALLINT,

  host TEXT NOT NULL,
  is_import BOOLEAN DEFAULT FALSE,
  is_quest BOOLEAN DEFAULT FALSE,

  boomed_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_boom_rankings_user
ON boom_command_rankings (user_id);

CREATE INDEX idx_boom_rankings_command
ON boom_command_rankings (command);

CREATE INDEX idx_boom_rankings_boomed_at
ON boom_command_rankings (boomed_at);

-- boom drought record view built from commands
CREATE VIEW boom_highest_droughts AS
SELECT DISTINCT ON (user_id)
    user_id,
    drought,
    boomed_at
FROM boom_command_rankings
WHERE drought IS NOT NULL
ORDER BY
    user_id,
    drought DESC,
    boomed_at DESC;

-- boom favorite table to track favorite per day
CREATE TABLE boom_favorites (
    day DATE PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    selected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- boom favorite entries function to return number of entries per user per day in tz
CREATE FUNCTION boom_favorite_entries(tz TEXT, max_entries INTEGER DEFAULT 8)
RETURNS TABLE (
    user_id BIGINT,
    entry_count INTEGER
)
LANGUAGE SQL
AS $$
WITH latest_day AS (
    SELECT MAX(DATE(boomed_at AT TIME ZONE tz)) AS boom_day
    FROM boom_command_rankings
)
SELECT
    b.user_id,
    LEAST(COUNT(*), GREATEST(max_entries, 1))::INTEGER AS entry_count
FROM boom_command_rankings b
JOIN latest_day d
  ON DATE(b.boomed_at AT TIME ZONE tz) = d.boom_day
GROUP BY b.user_id;
$$;

-- boom hall table to store all times users have hit 6/5 big booms
CREATE TABLE boom_hall (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  command TEXT NOT NULL,
  boomed_at TIMESTAMPTZ NOT NULL
);

-- boom avg/freq stats per command per user
CREATE VIEW boom_command_stats AS
SELECT
    user_id,
    command,
    COUNT(*)::INTEGER AS entry_count,
    AVG(ranking * multiplier)::NUMERIC(4,2) AS avg_score
FROM boom_command_rankings
GROUP BY user_id, command;

