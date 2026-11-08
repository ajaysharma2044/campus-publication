-- Down for 0005. UNSAFE: drops process graphs and the beat-review / seo-gate / information-gain records on page versions.
ALTER TABLE pages DROP COLUMN IF EXISTS primary_query;
ALTER TABLE serp_cache DROP COLUMN IF EXISTS demand_evidence;
ALTER TABLE page_versions DROP COLUMN IF EXISTS information_gain;
ALTER TABLE page_versions DROP COLUMN IF EXISTS seo_gate;
ALTER TABLE page_versions DROP COLUMN IF EXISTS beat_review;
DROP TABLE IF EXISTS process_node_claims;
DROP INDEX IF EXISTS process_nodes_graph_layer_idx;
DROP TABLE IF EXISTS process_nodes;
DROP TABLE IF EXISTS process_graphs;
