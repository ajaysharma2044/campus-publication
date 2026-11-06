-- 0003: continuous local run (specs/continuous-local-run.md R7, R8): ready queue, live ramp state, page tier.
ALTER TABLE pages ADD COLUMN ready_at TIMESTAMPTZ;                 -- passed every gate; publishable (R8)
ALTER TABLE pages ADD COLUMN niche_score NUMERIC(8,2);             -- from the sweet-spot queue (R22); orders live releases
ALTER TABLE pages ADD COLUMN tier SMALLINT NOT NULL DEFAULT 1 CHECK (tier IN (1,2));  -- R42
ALTER TABLE pages ADD COLUMN local_published_at TIMESTAMPTZ;       -- rendered to build/site + staging CMS
CREATE INDEX pages_ready_idx ON pages (ready_at) WHERE ready_at IS NOT NULL AND first_published_at IS NULL;

-- Live ramp state: one row. live_since starts the ramp clock the day the live domain is connected.
CREATE TABLE ramp_state (
    id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    live_since DATE,
    hold BOOLEAN NOT NULL DEFAULT FALSE,                            -- >20% of live pages unindexed after 14 days (R8)
    hold_reason TEXT,
    hold_rate_per_day INTEGER,                                      -- rate frozen while hold is set
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO ramp_state (id) VALUES (1);

-- Live releases: one row per page per go-live, for per-day ramp accounting and audit.
CREATE TABLE live_releases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    version_id UUID REFERENCES page_versions(id),
    released_on DATE NOT NULL,
    released_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    niche_score NUMERIC(8,2),
    kind TEXT NOT NULL CHECK (kind IN ('new','update'))
);
CREATE INDEX live_releases_day_idx ON live_releases (released_on, kind);
