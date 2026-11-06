-- 0006: reader-facing source titles (owner decision 2026-11-06, reader-first): the Sources list shows each official page's own title.
ALTER TABLE source_registry ADD COLUMN IF NOT EXISTS title TEXT;
