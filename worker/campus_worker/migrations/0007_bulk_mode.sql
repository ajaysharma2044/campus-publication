-- 0007: bulk mode (specs/bulk-mode.md, owner decision 2026-11-06): crawl runs, the question map, per-page pipeline state,
-- Message Batches bookkeeping and dossier runs. Crawled page text lives in fetch_snapshots (by content hash, with URL and date).
CREATE TABLE IF NOT EXISTS crawl_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id),
    place_id UUID REFERENCES places(id),
    run_id TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    stats JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS bulk_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id),
    place_id UUID REFERENCES places(id),
    topic_id UUID REFERENCES topics(id),
    entity_id UUID REFERENCES entities(id),
    cluster_id UUID REFERENCES intent_clusters(id),
    audience TEXT NOT NULL DEFAULT 'general',
    question TEXT NOT NULL,
    question_norm TEXT NOT NULL,
    answer_key TEXT NOT NULL,                      -- the dossier item that answers it: entity:<id>:<field family> | process:<key> | claim:<field>
    page_type TEXT NOT NULL,                       -- question_guide | entity_guide | process_guide | comparison
    origin TEXT NOT NULL,                          -- generated | cluster | yaml
    incumbent_class TEXT,                          -- strong_dedicated | weak | outdated | forum_only | none | unscanned
    incumbent_detail JSONB NOT NULL DEFAULT '{}'::jsonb,
    win_note TEXT,
    tier SMALLINT,
    order_rank INTEGER,
    status TEXT NOT NULL DEFAULT 'queued',         -- queued | planned | skipped | done
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS bulk_questions_key ON bulk_questions (COALESCE(institution_id::text, ''), COALESCE(place_id::text, ''), answer_key, audience);
CREATE INDEX IF NOT EXISTS bulk_questions_order ON bulk_questions (order_rank);

CREATE TABLE IF NOT EXISTS bulk_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID REFERENCES bulk_questions(id),
    page_id UUID REFERENCES pages(id),
    version_id UUID REFERENCES page_versions(id),
    path TEXT NOT NULL UNIQUE,
    page_type TEXT NOT NULL,
    stage TEXT NOT NULL DEFAULT 'planned',         -- planned | gathered | written | checked | verified | published | skipped | failed
    skip_reason TEXT,
    plan JSONB NOT NULL DEFAULT '{}'::jsonb,
    gathered JSONB,
    draft JSONB,
    checks JSONB,
    verdicts JSONB,
    write_batch_id TEXT,
    verify_batch_id TEXT,
    cost_minor INTEGER NOT NULL DEFAULT 0,
    run_id TEXT,
    sources_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS bulk_pages_stage ON bulk_pages (stage);

CREATE TABLE IF NOT EXISTS bulk_batches (
    id TEXT PRIMARY KEY,                           -- the API batch id, or fake:<n> / dry:<n>
    kind TEXT NOT NULL,                            -- extract | write | verify
    run_id TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'submitted',      -- submitted | in_progress | ended | failed
    request_count INTEGER NOT NULL DEFAULT 0,
    est_cost_minor INTEGER NOT NULL DEFAULT 0,
    actual_cost_minor INTEGER,
    usage JSONB NOT NULL DEFAULT '{}'::jsonb,
    results_processed BOOLEAN NOT NULL DEFAULT FALSE,
    custom_ids JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS dossier_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id),
    place_id UUID REFERENCES places(id),
    built_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    path TEXT,
    stats JSONB NOT NULL DEFAULT '{}'::jsonb,
    minutes NUMERIC,
    cost_minor INTEGER NOT NULL DEFAULT 0
);

ALTER TABLE fetch_snapshots ADD COLUMN IF NOT EXISTS extracted_at TIMESTAMPTZ;
ALTER TABLE fetch_snapshots ADD COLUMN IF NOT EXISTS extraction_batch_id TEXT;
ALTER TABLE source_registry ADD COLUMN IF NOT EXISTS crawl_section TEXT;
