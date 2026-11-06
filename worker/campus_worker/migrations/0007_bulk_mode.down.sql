ALTER TABLE source_registry DROP COLUMN IF EXISTS crawl_section;
ALTER TABLE fetch_snapshots DROP COLUMN IF EXISTS extraction_batch_id;
ALTER TABLE fetch_snapshots DROP COLUMN IF EXISTS extracted_at;
DROP TABLE IF EXISTS dossier_runs;
DROP TABLE IF EXISTS bulk_batches;
DROP TABLE IF EXISTS bulk_pages;
DROP TABLE IF EXISTS bulk_questions;
DROP TABLE IF EXISTS crawl_runs;
