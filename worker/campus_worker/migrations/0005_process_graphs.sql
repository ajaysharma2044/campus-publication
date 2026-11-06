-- 0005: layered process graphs and navigator (continuous-local-run R47), tier-2 and beat-review bookkeeping (R42, R38, R45).
CREATE TABLE process_graphs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id),
    topic_id UUID REFERENCES topics(id),
    key TEXT NOT NULL,                                     -- 'changing-majors', 'add-minor', 'transfer-credit', ...
    name TEXT NOT NULL,
    description TEXT,
    tool_path TEXT,                                        -- '/schools/<school>/<topic>/tools/<key>-navigator/'
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (institution_id, key)
);
CREATE TABLE process_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graph_id UUID NOT NULL REFERENCES process_graphs(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES process_nodes(id) ON DELETE CASCADE,
    layer SMALLINT NOT NULL CHECK (layer BETWEEN 0 AND 3),  -- L0 overview, L1 transition, L2 major/situation, L3 edge case
    key TEXT NOT NULL,
    label TEXT NOT NULL,
    from_state TEXT,                                       -- 'arts-sciences', 'engineering', ... (L1+)
    to_state TEXT,
    situation TEXT,                                        -- 'sophomore missing prerequisite', 'transfer student', ...
    rules JSONB NOT NULL DEFAULT '{}'::jsonb,              -- {steps[], prerequisites[], gpa_min, course_requirements[], deadlines[], forms[], offices[], exceptions[]}
    rules_hash TEXT NOT NULL,                              -- sha256 of the canonical rules; equal to the parent's → inherits, stores nothing new
    inherits_parent BOOLEAN NOT NULL DEFAULT FALSE,
    page_decision TEXT NOT NULL DEFAULT 'none' CHECK (page_decision IN ('standalone','section','none')),
    decision_reason TEXT,
    page_path TEXT,
    source_urls TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (graph_id, key)
);
CREATE INDEX process_nodes_graph_layer_idx ON process_nodes (graph_id, layer);
CREATE TABLE process_node_claims (
    node_id UUID NOT NULL REFERENCES process_nodes(id) ON DELETE CASCADE,
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'rule',                     -- 'rule' | 'deadline' | 'prerequisite' | 'office'
    PRIMARY KEY (node_id, claim_id)
);
-- page-level records for the writing-quality system and the SEO gate
ALTER TABLE page_versions ADD COLUMN beat_review JSONB;    -- R38 record: scores per item vs top 3 results, outcome
ALTER TABLE page_versions ADD COLUMN seo_gate JSONB;       -- R45 record: per-item pass/fail, outcome
ALTER TABLE page_versions ADD COLUMN information_gain JSONB;  -- R37: items with claim ids, competitors_say
ALTER TABLE pages ADD COLUMN primary_query TEXT;           -- R45 cannibalization check
