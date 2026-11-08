-- Steps pass bookkeeping: which batch (or ':error' / ':skipped' marker) covered the page, mirroring extraction_batch_id.
ALTER TABLE fetch_snapshots ADD COLUMN IF NOT EXISTS steps_batch_id TEXT;
