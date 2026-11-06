-- 0004: demand capture engine, town scope, access modes, open discovery (continuous-local-run R18–R24, R33–R36, R41, R46).

-- Places (towns, counties): the second scope next to institutions. Town entities carry place_id, never institution_id (R34).
CREATE TABLE places (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL CHECK (kind IN ('city','town','village','county','region')),
    state_code TEXT NOT NULL,
    country_code CHAR(2) NOT NULL DEFAULT 'US',
    parent_place_id UUID REFERENCES places(id),
    attributes JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE institutions ADD COLUMN place_id UUID REFERENCES places(id);           -- the school's town
ALTER TABLE entities ALTER COLUMN institution_id DROP NOT NULL;
ALTER TABLE entities ADD COLUMN place_id UUID REFERENCES places(id);
ALTER TABLE entities ADD CONSTRAINT entities_scope_chk CHECK (institution_id IS NOT NULL OR place_id IS NOT NULL);
ALTER TABLE entities ADD COLUMN source_id UUID REFERENCES source_registry(id);
ALTER TABLE entities ADD COLUMN source_url TEXT;
ALTER TABLE entities ADD COLUMN first_seen_at TIMESTAMPTZ;
ALTER TABLE entities ADD COLUMN last_seen_at TIMESTAMPTZ;
ALTER TABLE entities ADD COLUMN harvest_rule TEXT;                                -- which rule produced it (audit)
CREATE UNIQUE INDEX entities_place_slug_uniq ON entities (place_id, topic_id, slug) WHERE place_id IS NOT NULL;
ALTER TABLE source_registry ADD COLUMN place_id UUID REFERENCES places(id);
ALTER TABLE questions ADD COLUMN place_id UUID REFERENCES places(id);
ALTER TABLE questions ADD COLUMN pattern_key TEXT;                                -- R19 pattern that generated a hypothesis
ALTER TABLE questions ADD COLUMN pattern_version TEXT;
ALTER TABLE questions DROP CONSTRAINT questions_origin_check;
ALTER TABLE questions ADD CONSTRAINT questions_origin_check CHECK (origin IN
    ('official_faq','search_suggestion','related_question','discussion','competitor_gap','search_console','site_search','hypothesis',
     'first_party','structured_data','stackexchange','reddit_api'));
ALTER TABLE intent_clusters ADD COLUMN place_id UUID REFERENCES places(id);
ALTER TABLE pages ADD COLUMN place_id UUID REFERENCES places(id);

-- Topic taxonomy metadata (R33, R46).
ALTER TABLE topics ADD COLUMN scope TEXT NOT NULL DEFAULT 'school' CHECK (scope IN ('school','town','both'));
ALTER TABLE topics ADD COLUMN audiences TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE topics ADD COLUMN freshness_risk TEXT NOT NULL DEFAULT 'medium' CHECK (freshness_risk IN ('low','medium','high'));
ALTER TABLE topics ADD COLUMN source_families TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE topics ADD COLUMN auto_created BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE topics ADD COLUMN created_from TEXT;                                  -- cluster id / question sample for auto topics
ALTER TABLE topics ADD COLUMN parent_key TEXT;                                    -- audience topic sets hang under a shared topic

-- Access modes (R35): exactly one per source, enforced in code.
ALTER TABLE source_permissions DROP CONSTRAINT source_permissions_access_mode_check;
ALTER TABLE source_permissions ADD CONSTRAINT source_permissions_access_mode_check CHECK (access_mode IN
    ('search_observation','fetch_permitted','api_authorized','disabled','public_http','feed','export_import'));
ALTER TABLE source_permissions ADD COLUMN terms_checked_at TIMESTAMPTZ;
ALTER TABLE source_permissions ADD COLUMN robots_checked_at TIMESTAMPTZ;
ALTER TABLE source_permissions ADD COLUMN robots_allows BOOLEAN;
ALTER TABLE source_permissions ADD COLUMN attribution_required TEXT;             -- e.g. 'CC BY-SA 4.0' for Stack Exchange

-- Search-result cache (R26): one row per normalized query; never re-searched inside the window.
CREATE TABLE serp_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_norm TEXT NOT NULL UNIQUE,
    query_text TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    provider TEXT NOT NULL DEFAULT 'websearch',
    results JSONB NOT NULL,
    follow_up_questions JSONB NOT NULL DEFAULT '[]'::jsonb,
    community_occurrences JSONB NOT NULL DEFAULT '[]'::jsonb,
    navigational BOOLEAN NOT NULL DEFAULT FALSE
);

-- Cluster-level engine state (R21, R22).
ALTER TABLE intent_clusters ADD COLUMN agi SMALLINT CHECK (agi BETWEEN 0 AND 5);
ALTER TABLE intent_clusters ADD COLUMN agi_detail JSONB;
ALTER TABLE intent_clusters ADD COLUMN demand_points INTEGER NOT NULL DEFAULT 0;
ALTER TABLE intent_clusters ADD COLUMN d_score SMALLINT CHECK (d_score BETWEEN 0 AND 5);
ALTER TABLE intent_clusters ADD COLUMN g_est SMALLINT CHECK (g_est BETWEEN 0 AND 5);
ALTER TABLE intent_clusters ADD COLUMN e_est SMALLINT CHECK (e_est BETWEEN 0 AND 5);
ALTER TABLE intent_clusters ADD COLUMN niche_score NUMERIC(8,2);
ALTER TABLE intent_clusters ADD COLUMN queue_state TEXT NOT NULL DEFAULT 'candidate'
    CHECK (queue_state IN ('candidate','needs_intel','sweet_spot','watch','reject','navigational','in_production','done'));
ALTER TABLE intent_clusters ADD COLUMN queue_reason TEXT;
ALTER TABLE intent_clusters ADD COLUMN seasonality_urgency SMALLINT NOT NULL DEFAULT 0;
ALTER TABLE intent_clusters ADD COLUMN freshness_risk SMALLINT NOT NULL DEFAULT 0;
ALTER TABLE intent_clusters ADD COLUMN best_variant TEXT;
ALTER TABLE intent_clusters ADD COLUMN last_intel_at TIMESTAMPTZ;
ALTER TABLE intent_clusters ADD COLUMN capture_format TEXT CHECK (capture_format IN ('entity_guide','guide','comparison','calculator','section','tool'));
CREATE INDEX intent_clusters_queue_idx ON intent_clusters (queue_state, niche_score DESC);

-- Strategies and query targets (R14, R45 cannibalization check).
CREATE TABLE strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id),
    place_id UUID REFERENCES places(id),
    topic_id UUID REFERENCES topics(id),
    version INTEGER NOT NULL DEFAULT 1,
    doc JSONB NOT NULL,
    md_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE query_targets (
    query_norm TEXT PRIMARY KEY,
    page_path TEXT NOT NULL,
    query_group TEXT NOT NULL,
    strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX query_targets_page_idx ON query_targets (page_path);

-- Lane accounting per run (R24) and digest events (R9, R46).
CREATE TABLE lane_state (
    run_id TEXT NOT NULL,
    lane TEXT NOT NULL CHECK (lane IN ('production','discovery','maintenance','checks')),
    picks INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, lane)
);
CREATE TABLE digest_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    run_id TEXT,
    kind TEXT NOT NULL,                                                            -- 'topic_created','page_published','page_held','claim_verified',...
    detail JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX digest_events_day_idx ON digest_events (created_at);

-- Harvest sources: which registered sources feed entity harvesting, with their rules (R18, R34).
CREATE TABLE harvest_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES source_registry(id) ON DELETE CASCADE,
    rule_key TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    topic_key TEXT NOT NULL,
    rule JSONB NOT NULL,
    last_harvested_at TIMESTAMPTZ,
    last_count INTEGER,
    UNIQUE (source_id, rule_key)
);
