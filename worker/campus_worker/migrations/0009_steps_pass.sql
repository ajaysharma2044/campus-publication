-- Verbatim process-steps pass (subscription-only run, 2026-11-07): each step of a procedure becomes its own quoted claim
-- (process.<key>.step_NN); this marks which page snapshots the pass has covered.
ALTER TABLE fetch_snapshots ADD COLUMN IF NOT EXISTS steps_extracted_at TIMESTAMPTZ;
