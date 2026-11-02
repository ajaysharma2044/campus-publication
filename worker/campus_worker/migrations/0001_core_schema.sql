-- 0001_core_schema: research, provenance, discovery, editorial, operations (SPEC §14).
-- Conventions: immutable UUID ids; UTC timestamptz; money as integer minor units with currency;
-- academic year / effective dates separate from fetch time; institution_id + campus_id on every
-- school-scoped record; enums enforced via CHECK constraints for portability.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------- identity
CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    institution_type TEXT NOT NULL CHECK (institution_type IN
        ('university','college','community_college','technical_college','graduate_school','system','other')),
    control TEXT CHECK (control IN ('public','private_nonprofit','private_forprofit','unknown')),
    is_system BOOLEAN NOT NULL DEFAULT FALSE,            -- a system is not a campus (SPEC §07)
    parent_system_id UUID REFERENCES institutions(id),
    country_code CHAR(2) NOT NULL DEFAULT 'US',
    state_code TEXT,
    city TEXT,
    primary_domain TEXT,
    identity_status TEXT NOT NULL DEFAULT 'pending_verification'
        CHECK (identity_status IN ('verified','pending_verification','synthetic_fixture','merged','closed')),
    merged_into_id UUID REFERENCES institutions(id),
    closed_on DATE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX institutions_name_idx ON institutions (lower(canonical_name));

CREATE TABLE institution_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    alias TEXT NOT NULL,
    alias_type TEXT NOT NULL CHECK (alias_type IN ('former_name','abbreviation','colloquial','domain','other')),
    valid_from DATE,
    valid_to DATE,
    UNIQUE (institution_id, alias, alias_type)
);

CREATE TABLE institution_external_ids (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    system_name TEXT NOT NULL,                             -- e.g. 'ipeds_unitid', 'ope_id', 'ror'
    external_id TEXT NOT NULL,
    source_release TEXT,                                   -- e.g. 'IPEDS HD2024 (provisional)'
    source_release_date DATE,
    retrieved_at TIMESTAMPTZ,
    UNIQUE (system_name, external_id)
);

CREATE TABLE campuses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    is_main BOOLEAN NOT NULL DEFAULT FALSE,
    city TEXT,
    state_code TEXT,
    timezone TEXT NOT NULL DEFAULT 'America/New_York',
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','closed','merged','synthetic_fixture')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (institution_id, slug)
);

CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,                              -- 'housing', 'transfer', ...
    label TEXT NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE school_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    campus_id UUID REFERENCES campuses(id),
    locale TEXT NOT NULL DEFAULT 'en-US',
    timezone TEXT NOT NULL DEFAULT 'America/New_York',
    academic_calendar TEXT NOT NULL DEFAULT 'semester'
        CHECK (academic_calendar IN ('semester','quarter','trimester','rolling','mixed','unknown')),
    source_domains TEXT[] NOT NULL DEFAULT '{}',
    permitted_connectors TEXT[] NOT NULL DEFAULT '{}',
    audiences TEXT[] NOT NULL DEFAULT '{}',
    coverage_status TEXT NOT NULL DEFAULT 'registry_only'
        CHECK (coverage_status IN ('registry_only','onboarding','pilot','active','paused')),
    is_underserved BOOLEAN NOT NULL DEFAULT FALSE,        -- eligible for exploration share
    refresh_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (institution_id, campus_id)
);

-- topic applicability per school: not_applicable is distinct from unknown (SPEC §07)
CREATE TABLE school_topic_applicability (
    school_config_id UUID NOT NULL REFERENCES school_configs(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES topics(id),
    applicability TEXT NOT NULL CHECK (applicability IN ('applicable','not_applicable','unknown')),
    rationale TEXT,
    PRIMARY KEY (school_config_id, topic_id)
);

CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id),
    campus_id UUID REFERENCES campuses(id),
    topic_id UUID NOT NULL REFERENCES topics(id),
    entity_type TEXT NOT NULL,                              -- 'residence_hall','program','meal_plan','parking_lot',...
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}'::jsonb,         -- non-claim descriptive attributes only
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive','synthetic_fixture')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (institution_id, topic_id, slug)
);
CREATE INDEX entities_inst_topic_idx ON entities (institution_id, topic_id);

-- ---------------------------------------------------------------- sources
CREATE TABLE source_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_pattern TEXT NOT NULL UNIQUE,                   -- 'scl.cornell.edu' or '*.cornell.edu'
    publisher TEXT,
    connector TEXT NOT NULL,                               -- 'official_html','official_pdf','feed','discussion',...
    access_mode TEXT NOT NULL CHECK (access_mode IN ('public_http','api_authorized','feed','export_import','disabled')),
    permission_state TEXT NOT NULL CHECK (permission_state IN ('allowed','allowed_with_limits','disabled','pending_authorization')),
    retention_policy TEXT NOT NULL DEFAULT 'excerpts_only'
        CHECK (retention_policy IN ('full_text','excerpts_only','hashes_only','none')),
    rate_limit_per_minute INTEGER NOT NULL DEFAULT 6,
    terms_reference TEXT,
    notes TEXT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE source_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id),
    campus_id UUID REFERENCES campuses(id),
    canonical_url TEXT NOT NULL UNIQUE,
    publisher TEXT,
    source_kind TEXT NOT NULL CHECK (source_kind IN
        ('official_html','official_pdf','catalog','calendar','feed','property','service','discussion','search_snippet','first_party','dataset')),
    permission_id UUID REFERENCES source_permissions(id),
    reliability TEXT NOT NULL DEFAULT 'unrated' CHECK (reliability IN ('official','authoritative_third_party','attributed_experience','unrated','unreliable')),
    source_family TEXT,                                    -- dedupe mirrors/syndication
    refresh_interval_hours INTEGER NOT NULL DEFAULT 168,
    next_refresh_at TIMESTAMPTZ,
    health TEXT NOT NULL DEFAULT 'unknown' CHECK (health IN ('healthy','degraded','blocked','gone','unknown')),
    last_fetched_at TIMESTAMPTZ,
    last_changed_at TIMESTAMPTZ,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX source_registry_refresh_idx ON source_registry (next_refresh_at) WHERE health <> 'gone';

CREATE TABLE fetch_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES source_registry(id) ON DELETE CASCADE,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    final_url TEXT NOT NULL,
    http_status INTEGER,
    content_type TEXT,
    content_hash TEXT NOT NULL,                            -- hash of material (nav-stripped) content
    raw_hash TEXT,                                         -- hash of raw bytes
    byte_size INTEGER,
    etag TEXT,
    last_modified TEXT,
    extraction_confidence NUMERIC(4,3) CHECK (extraction_confidence BETWEEN 0 AND 1),
    retained_text TEXT,                                    -- only if permission allows
    retained_tables JSONB,
    material_change BOOLEAN,                               -- vs previous snapshot
    outcome TEXT NOT NULL CHECK (outcome IN ('ok','unchanged','blocked','error','redirect_rejected','oversized','unexpected_type','parse_failed')),
    error_detail TEXT
);
CREATE INDEX fetch_snapshots_source_idx ON fetch_snapshots (source_id, fetched_at DESC);

-- ---------------------------------------------------------------- claims
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id),
    campus_id UUID REFERENCES campuses(id),
    entity_id UUID REFERENCES entities(id),
    topic_id UUID NOT NULL REFERENCES topics(id),
    field TEXT NOT NULL,                                   -- 'rate.double_room', 'ac', 'eligibility.transfer', ...
    value_type TEXT NOT NULL CHECK (value_type IN ('money','integer','decimal','boolean','text','date','enum','range_money','duration')),
    value_text TEXT,
    value_number NUMERIC,
    value_number_high NUMERIC,                             -- for ranges
    value_bool BOOLEAN,
    value_date DATE,
    unit TEXT,                                             -- 'minor_units','sqft','minutes', ...
    currency CHAR(3),
    billing_period TEXT CHECK (billing_period IN ('per_month','per_semester','per_academic_year','per_term','per_year','one_time','per_week','per_day','unknown')),
    price_basis TEXT CHECK (price_basis IN ('per_person','per_unit','per_bed','unknown')),
    room_type TEXT,                                        -- preserve floor-plan/room distinctions
    audience_applicability TEXT[] NOT NULL DEFAULT '{}',   -- empty = all
    academic_year TEXT,                                    -- '2026-27'
    term TEXT,
    effective_from DATE,
    effective_to DATE,
    evidence_category TEXT NOT NULL CHECK (evidence_category IN
        ('verified_fact','estimate','attributed_experience','unknown','not_applicable','stale','conflicted')),
    is_critical BOOLEAN NOT NULL DEFAULT FALSE,
    conflict_status TEXT NOT NULL DEFAULT 'none' CHECK (conflict_status IN ('none','open','resolved','scoped_unresolved')),
    extraction_method TEXT NOT NULL CHECK (extraction_method IN ('deterministic','model','manual','import')),
    extraction_model TEXT,
    extraction_confidence NUMERIC(4,3),
    retrieved_at TIMESTAMPTZ NOT NULL,
    verification_due_at TIMESTAMPTZ,
    superseded_by_id UUID REFERENCES claims(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (value_type <> 'money' OR (currency IS NOT NULL AND unit = 'minor_units' AND value_number = trunc(value_number)))
);
CREATE INDEX claims_entity_field_idx ON claims (entity_id, field) WHERE superseded_by_id IS NULL;
CREATE INDEX claims_inst_topic_idx ON claims (institution_id, topic_id);
CREATE INDEX claims_due_idx ON claims (verification_due_at) WHERE superseded_by_id IS NULL;

CREATE TABLE claim_sources (
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    snapshot_id UUID NOT NULL REFERENCES fetch_snapshots(id),
    excerpt TEXT,                                          -- staff-only; respects retention policy
    locator TEXT,                                          -- 'p.3 table 2 row 4' / css path
    PRIMARY KEY (claim_id, snapshot_id)
);

CREATE TABLE conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id),
    claim_a_id UUID NOT NULL REFERENCES claims(id),
    claim_b_id UUID NOT NULL REFERENCES claims(id),
    conflict_type TEXT NOT NULL CHECK (conflict_type IN ('value','scope','academic_year','eligibility','unit','source_precedence')),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','resolved','scoped_unresolved')),
    resolution TEXT,
    resolved_claim_id UUID REFERENCES claims(id),
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    CHECK (claim_a_id <> claim_b_id)
);
CREATE INDEX conflicts_open_idx ON conflicts (institution_id) WHERE status = 'open';

-- ---------------------------------------------------------------- discovery
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id),
    campus_id UUID REFERENCES campuses(id),
    topic_id UUID REFERENCES topics(id),
    entity_id UUID REFERENCES entities(id),
    raw_text TEXT NOT NULL,
    normalized_text TEXT NOT NULL,
    origin TEXT NOT NULL CHECK (origin IN ('official_faq','search_suggestion','related_question','discussion','competitor_gap','search_console','site_search','hypothesis')),
    is_hypothesis BOOLEAN NOT NULL DEFAULT FALSE,          -- generated, not observed (SPEC §10)
    audience TEXT,
    constraints TEXT[] NOT NULL DEFAULT '{}',
    observed_at TIMESTAMPTZ,
    source_ref TEXT,                                       -- opaque reference; never a user identity
    occurrence_key TEXT,                                   -- dedupe of same post/crosspost
    cluster_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX questions_norm_idx ON questions (institution_id, normalized_text);

CREATE TABLE intent_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id),
    campus_id UUID REFERENCES campuses(id),
    topic_id UUID REFERENCES topics(id),
    entity_id UUID REFERENCES entities(id),
    label TEXT NOT NULL,
    answer_key TEXT NOT NULL,                              -- what resolves it; clusters merge when identical
    audience TEXT,
    task TEXT,
    independent_occurrences INTEGER NOT NULL DEFAULT 0,
    observed_count INTEGER NOT NULL DEFAULT 0,
    hypothesis_count INTEGER NOT NULL DEFAULT 0,
    coverage_state TEXT NOT NULL DEFAULT 'unknown' CHECK (coverage_state IN ('answered','partially_answered','unknown','not_applicable','stale','researching')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE questions ADD CONSTRAINT questions_cluster_fk FOREIGN KEY (cluster_id) REFERENCES intent_clusters(id);

CREATE TABLE demand_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cluster_id UUID NOT NULL REFERENCES intent_clusters(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    query_text TEXT NOT NULL,
    geography TEXT NOT NULL,
    language TEXT NOT NULL,
    window_start DATE NOT NULL,
    window_end DATE NOT NULL,
    monthly_breakdown JSONB,
    volume_low INTEGER,                                    -- NULL = unknown/suppressed, never 0
    volume_high INTEGER,
    is_suppressed BOOLEAN NOT NULL DEFAULT FALSE,
    variant_group TEXT,                                    -- close variants share a group; never summed
    retrieved_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE serp_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cluster_id UUID NOT NULL REFERENCES intent_clusters(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    locale TEXT NOT NULL,
    device TEXT NOT NULL CHECK (device IN ('desktop','mobile')),
    results JSONB NOT NULL,                                -- [{position,url,result_type,answer_quality,freshness,...}]
    direct_answer_quality TEXT CHECK (direct_answer_quality IN ('complete','partial','none','navigational_official')),
    missing_contribution TEXT,
    provider TEXT NOT NULL
);

CREATE TABLE coverage_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_type TEXT NOT NULL,
    from_id UUID NOT NULL,
    to_type TEXT NOT NULL,
    to_id UUID NOT NULL,
    relation TEXT NOT NULL,                                -- 'answers','follows_up','compares','applies_to'
    state TEXT NOT NULL DEFAULT 'unknown' CHECK (state IN ('answered','unknown','not_applicable','stale','worth_researching')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (from_type, from_id, to_type, to_id, relation)
);

CREATE TABLE opportunity_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cluster_id UUID NOT NULL REFERENCES intent_clusters(id) ON DELETE CASCADE,
    scored_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    demand SMALLINT CHECK (demand BETWEEN 0 AND 5),
    answer_gap SMALLINT CHECK (answer_gap BETWEEN 0 AND 5),
    winnability SMALLINT CHECK (winnability BETWEEN 0 AND 5),
    evidence_advantage SMALLINT CHECK (evidence_advantage BETWEEN 0 AND 5),
    commercial SMALLINT CHECK (commercial BETWEEN 0 AND 5),
    priority NUMERIC(5,2),                                 -- NULL if any input NULL (unassessed)
    confidence TEXT CHECK (confidence IN ('low','medium','high')),
    effort_research SMALLINT, effort_build SMALLINT, effort_maintain SMALLINT,
    observations JSONB NOT NULL DEFAULT '{}'::jsonb,       -- per-score justification
    decision TEXT NOT NULL CHECK (decision IN ('advance','update','improve_section','new_tool','merge','watch','reject','hold')),
    decision_rationale TEXT,
    editorial_exception BOOLEAN NOT NULL DEFAULT FALSE,
    exception_rationale TEXT,
    existing_coverage_checked UUID[] NOT NULL DEFAULT '{}',
    scorer_model TEXT
);

-- ---------------------------------------------------------------- editorial
CREATE TABLE briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id),
    campus_id UUID REFERENCES campuses(id),
    cluster_id UUID REFERENCES intent_clusters(id),
    opportunity_id UUID REFERENCES opportunity_scores(id),
    page_format TEXT NOT NULL CHECK (page_format IN ('guide','entity_profile','comparison','tool','topic_hub','school_hub','explainer')),
    audience TEXT NOT NULL,
    reader_decision TEXT NOT NULL,
    verified_answer TEXT NOT NULL,
    unique_contribution TEXT NOT NULL,
    critical_claim_ids UUID[] NOT NULL DEFAULT '{}',
    unresolved_facts TEXT[] NOT NULL DEFAULT '{}',
    exceptions TEXT[] NOT NULL DEFAULT '{}',
    structure JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_subjective_evidence TEXT[] NOT NULL DEFAULT '{}',
    next_tasks TEXT[] NOT NULL DEFAULT '{}',
    overlap_page_ids UUID[] NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','approved','rejected','superseded')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id),
    campus_id UUID REFERENCES campuses(id),
    topic_id UUID REFERENCES topics(id),
    entity_id UUID REFERENCES entities(id),
    page_format TEXT NOT NULL CHECK (page_format IN ('guide','entity_profile','comparison','tool','topic_hub','school_hub','explainer','policy','home')),
    slug TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,                             -- '/schools/cornell/housing/mews-hall/'
    audience TEXT,
    status TEXT NOT NULL DEFAULT 'planned' CHECK (status IN ('planned','drafting','held','staged','published','unpublished','redirected')),
    current_version_id UUID,
    cms_external_id TEXT,                                  -- WP post id, stable
    cms_content_hash TEXT,
    redirect_to_path TEXT,
    first_published_at TIMESTAMPTZ,
    last_material_update_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX pages_inst_idx ON pages (institution_id, topic_id);

CREATE TABLE page_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    version_no INTEGER NOT NULL,
    brief_id UUID REFERENCES briefs(id),
    headline TEXT NOT NULL,
    deck TEXT,
    body_markdown TEXT NOT NULL,
    body_html TEXT,
    structured JSONB NOT NULL DEFAULT '{}'::jsonb,         -- fact tables, sources, related links
    byline TEXT NOT NULL DEFAULT 'Publication desk',       -- truthful credit; never an invented person
    production_note TEXT,                                  -- automation/review disclosure
    content_hash TEXT NOT NULL,
    writer_model TEXT, editor_model TEXT, verifier_model TEXT,
    gate_status TEXT NOT NULL DEFAULT 'pending' CHECK (gate_status IN ('pending','passed','failed','held')),
    gate_findings JSONB NOT NULL DEFAULT '[]'::jsonb,
    rubric JSONB,                                          -- {clarity:4,...,total:22}
    is_material_change BOOLEAN NOT NULL DEFAULT TRUE,
    change_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (page_id, version_no)
);
ALTER TABLE pages ADD CONSTRAINT pages_current_version_fk FOREIGN KEY (current_version_id) REFERENCES page_versions(id);

CREATE TABLE page_claims (
    page_version_id UUID NOT NULL REFERENCES page_versions(id) ON DELETE CASCADE,
    claim_id UUID NOT NULL REFERENCES claims(id),
    usage TEXT NOT NULL CHECK (usage IN ('fact_table','prose','calculation','comparison')),
    PRIMARY KEY (page_version_id, claim_id, usage)
);

CREATE TABLE dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upstream_type TEXT NOT NULL CHECK (upstream_type IN ('claim','source','entity','page','tool_config')),
    upstream_id UUID NOT NULL,
    downstream_type TEXT NOT NULL CHECK (downstream_type IN ('page','page_version','tool_config','comparison','recommendation')),
    downstream_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (upstream_type, upstream_id, downstream_type, downstream_id)
);
CREATE INDEX dependencies_up_idx ON dependencies (upstream_type, upstream_id);

CREATE TABLE tool_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_key TEXT NOT NULL,                                -- 'comparison','total_cost_calculator'
    institution_id UUID REFERENCES institutions(id),
    campus_id UUID REFERENCES campuses(id),
    topic_id UUID REFERENCES topics(id),
    version INTEGER NOT NULL DEFAULT 1,
    config JSONB NOT NULL,                                 -- inputs, method, limitations, entity ids
    method_description TEXT NOT NULL,
    limitations TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','tested','published','retired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tool_key, institution_id, campus_id, topic_id, version)
);

-- ---------------------------------------------------------------- operations
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL,
    institution_id UUID REFERENCES institutions(id),
    campus_id UUID REFERENCES campuses(id),
    idempotency_key TEXT NOT NULL UNIQUE,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    priority INTEGER NOT NULL DEFAULT 50,
    state TEXT NOT NULL DEFAULT 'queued' CHECK (state IN ('queued','leased','succeeded','retry_wait','held','dead_letter','cancelled')),
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    not_before TIMESTAMPTZ NOT NULL DEFAULT now(),
    lease_owner TEXT,
    lease_expires_at TIMESTAMPTZ,
    depends_on UUID[] NOT NULL DEFAULT '{}',
    hold_reason TEXT,                                      -- machine-readable, e.g. 'missing_evidence'
    hold_retry_condition TEXT,
    hold_owner TEXT,
    last_error TEXT,
    estimated_cost_minor INTEGER,                          -- NULL = unpriced → cannot run if paid
    is_paid BOOLEAN NOT NULL DEFAULT FALSE,
    model_role TEXT,
    parent_job_id UUID REFERENCES jobs(id),
    delegation_depth INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX jobs_dispatch_idx ON jobs (state, not_before, priority DESC) WHERE state IN ('queued','retry_wait');
CREATE INDEX jobs_lease_idx ON jobs (lease_expires_at) WHERE state = 'leased';

CREATE TABLE runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    attempt INTEGER NOT NULL,
    role TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running','succeeded','failed','held','lost_lease','reconciled')),
    model_role TEXT,
    requested_model TEXT,
    resolved_model TEXT,                                   -- exact id used (SPEC §36)
    fallback_rationale TEXT,
    escalation_level INTEGER NOT NULL DEFAULT 0,
    decision TEXT,
    output_ref TEXT,                                       -- artifact path/id; large content not inline
    validation_errors JSONB,
    usage JSONB,                                           -- tokens in/out/cached, tool calls, retries
    worker_id TEXT,
    UNIQUE (job_id, attempt)
);

CREATE TABLE usage_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    day DATE NOT NULL,
    month CHAR(7) NOT NULL,                                -- 'YYYY-MM'
    job_id UUID REFERENCES jobs(id),
    run_id UUID REFERENCES runs(id),
    provider TEXT NOT NULL,                                -- 'anthropic','search','routing','keyword','other'
    kind TEXT NOT NULL CHECK (kind IN ('reservation','actual','release','adjustment')),
    amount_minor INTEGER NOT NULL,                         -- positive = spend/reserve, negative = release
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    priced BOOLEAN NOT NULL DEFAULT TRUE,                  -- FALSE = unpriced usage recorded for visibility
    detail JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX usage_ledger_day_idx ON usage_ledger (day);
CREATE INDEX usage_ledger_month_idx ON usage_ledger (month);

CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,
    area TEXT NOT NULL CHECK (area IN ('headline','layout','ads','related_links','tool','other')),
    hypothesis TEXT NOT NULL,
    allocation JSONB NOT NULL,                             -- {"control":50,"variant":50}
    primary_metric TEXT NOT NULL,
    guardrails JSONB NOT NULL DEFAULT '[]'::jsonb,
    minimum_observation TEXT NOT NULL,                     -- '14 days and 2000 sessions'
    stopping_rule TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned' CHECK (status IN ('planned','running','stopped','concluded','rolled_back')),
    outcome TEXT,
    rollback_note TEXT,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE analytics_aggregates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    day DATE NOT NULL,
    page_id UUID REFERENCES pages(id),
    template TEXT,
    institution_id UUID REFERENCES institutions(id),
    event_name TEXT NOT NULL,
    device_class TEXT,
    experiment_key TEXT,
    count INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'first_party',
    UNIQUE (day, page_id, event_name, device_class, experiment_key, source)
);

CREATE TABLE revenue_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider TEXT NOT NULL,                                -- 'adsense','direct_sponsorship'
    report_date DATE NOT NULL,
    granularity TEXT NOT NULL CHECK (granularity IN ('site','page','ad_unit')),
    page_id UUID REFERENCES pages(id),
    pageviews INTEGER,
    ad_impressions INTEGER,
    viewable_impressions INTEGER,
    clicks INTEGER,
    earnings_minor INTEGER,                                -- net publisher earnings as reported
    currency CHAR(3) NOT NULL,
    is_estimated BOOLEAN NOT NULL DEFAULT TRUE,            -- network reports lag and revise
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    raw JSONB,
    UNIQUE (provider, report_date, granularity, page_id)
);

CREATE TABLE exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    severity TEXT NOT NULL CHECK (severity IN ('info','warning','error','critical')),
    category TEXT NOT NULL,                                -- 'integration','budget','source','gate','security'
    job_id UUID REFERENCES jobs(id),
    institution_id UUID REFERENCES institutions(id),
    message TEXT NOT NULL,
    detail JSONB NOT NULL DEFAULT '{}'::jsonb,
    owner TEXT NOT NULL DEFAULT 'system',
    resolved_at TIMESTAMPTZ
);
CREATE INDEX exceptions_open_idx ON exceptions (severity, occurred_at DESC) WHERE resolved_at IS NULL;

CREATE TABLE correction_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID REFERENCES pages(id),
    page_version_id UUID REFERENCES page_versions(id),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    sanitized_text TEXT NOT NULL,                          -- sanitized, length-capped; never in analytics
    contact_hash TEXT,                                     -- optional, hashed, isolated from analytics
    submitter_ip_hash TEXT,                                -- for rate limiting only; short retention
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new','triaged','corrected','rejected','duplicate')),
    resolution TEXT,
    resolved_at TIMESTAMPTZ
);

-- heartbeat / operating status
CREATE TABLE heartbeats (
    component TEXT PRIMARY KEY,                            -- 'scheduler','collector','publisher'
    last_started_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    last_status TEXT,                                      -- executing|waiting|usage_paused|blocked|failed|scheduled
    detail JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- seed topics (national modules, SPEC §03)
INSERT INTO topics (key, label, sort_order) VALUES
 ('admissions','Admissions and applications',10),
 ('transfer','Transfer pathways',20),
 ('programs','Academic programs',30),
 ('courses','Course enrollment and prerequisites',40),
 ('costs_aid','Costs and financial aid',50),
 ('housing','Housing',60),
 ('dining','Dining',70),
 ('transportation','Transportation and parking',80),
 ('clubs_events','Clubs and events',90),
 ('services','Campus services',100),
 ('careers','Internships and career opportunities',110),
 ('accessibility','Accessibility',120),
 ('daily_life','Arrival and daily life',130);
