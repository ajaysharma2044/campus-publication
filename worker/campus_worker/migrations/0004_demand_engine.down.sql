-- Down for 0004. UNSAFE: drops places, serp_cache, strategies, query_targets, lane_state, digest_events, harvest_sources and
-- the engine columns (harvest provenance, hypotheses pattern keys, cluster scores). Restore from backup if needed.
DROP TABLE IF EXISTS harvest_sources;
DROP TABLE IF EXISTS digest_events;
DROP TABLE IF EXISTS lane_state;
DROP TABLE IF EXISTS query_targets;
DROP TABLE IF EXISTS strategies;
DROP INDEX IF EXISTS intent_clusters_queue_idx;
ALTER TABLE intent_clusters DROP COLUMN IF EXISTS capture_format, DROP COLUMN IF EXISTS last_intel_at, DROP COLUMN IF EXISTS best_variant,
    DROP COLUMN IF EXISTS freshness_risk, DROP COLUMN IF EXISTS seasonality_urgency, DROP COLUMN IF EXISTS queue_reason, DROP COLUMN IF EXISTS queue_state,
    DROP COLUMN IF EXISTS niche_score, DROP COLUMN IF EXISTS e_est, DROP COLUMN IF EXISTS g_est, DROP COLUMN IF EXISTS d_score,
    DROP COLUMN IF EXISTS demand_points, DROP COLUMN IF EXISTS agi_detail, DROP COLUMN IF EXISTS agi, DROP COLUMN IF EXISTS place_id;
DROP TABLE IF EXISTS serp_cache;
ALTER TABLE source_permissions DROP COLUMN IF EXISTS attribution_required, DROP COLUMN IF EXISTS robots_allows,
    DROP COLUMN IF EXISTS robots_checked_at, DROP COLUMN IF EXISTS terms_checked_at;
ALTER TABLE source_permissions DROP CONSTRAINT IF EXISTS source_permissions_access_mode_check;
ALTER TABLE source_permissions ADD CONSTRAINT source_permissions_access_mode_check CHECK (access_mode IN ('public_http','api_authorized','feed','export_import','disabled'));
ALTER TABLE topics DROP COLUMN IF EXISTS parent_key, DROP COLUMN IF EXISTS created_from, DROP COLUMN IF EXISTS auto_created,
    DROP COLUMN IF EXISTS source_families, DROP COLUMN IF EXISTS freshness_risk, DROP COLUMN IF EXISTS audiences, DROP COLUMN IF EXISTS scope;
ALTER TABLE pages DROP COLUMN IF EXISTS place_id;
ALTER TABLE questions DROP CONSTRAINT IF EXISTS questions_origin_check;
ALTER TABLE questions ADD CONSTRAINT questions_origin_check CHECK (origin IN ('official_faq','search_suggestion','related_question','discussion','competitor_gap','search_console','site_search','hypothesis'));
ALTER TABLE questions DROP COLUMN IF EXISTS pattern_version, DROP COLUMN IF EXISTS pattern_key, DROP COLUMN IF EXISTS place_id;
ALTER TABLE source_registry DROP COLUMN IF EXISTS place_id;
DROP INDEX IF EXISTS entities_place_slug_uniq;
ALTER TABLE entities DROP COLUMN IF EXISTS harvest_rule, DROP COLUMN IF EXISTS last_seen_at, DROP COLUMN IF EXISTS first_seen_at,
    DROP COLUMN IF EXISTS source_url, DROP COLUMN IF EXISTS source_id;
ALTER TABLE entities DROP CONSTRAINT IF EXISTS entities_scope_chk;
ALTER TABLE entities DROP COLUMN IF EXISTS place_id;
ALTER TABLE entities ALTER COLUMN institution_id SET NOT NULL;
ALTER TABLE institutions DROP COLUMN IF EXISTS place_id;
DROP TABLE IF EXISTS places;
