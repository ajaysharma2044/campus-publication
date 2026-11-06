-- Down for 0003. UNSAFE: drops live_releases (go-live audit) and ramp_state; restore from backup if needed.
DROP TABLE IF EXISTS live_releases;
DROP TABLE IF EXISTS ramp_state;
DROP INDEX IF EXISTS pages_ready_idx;
ALTER TABLE pages DROP COLUMN IF EXISTS local_published_at;
ALTER TABLE pages DROP COLUMN IF EXISTS tier;
ALTER TABLE pages DROP COLUMN IF EXISTS niche_score;
ALTER TABLE pages DROP COLUMN IF EXISTS ready_at;
