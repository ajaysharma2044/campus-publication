-- Down for 0002. Safe: drops two nullable/default columns; no data beyond flags is lost.
DROP INDEX IF EXISTS pages_revalidation_idx;
ALTER TABLE pages DROP COLUMN IF EXISTS revalidation_reason;
ALTER TABLE pages DROP COLUMN IF EXISTS revalidation_required;
