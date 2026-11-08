-- 0002: revalidation flags on pages for source-change propagation (SPEC §13, §28)
ALTER TABLE pages ADD COLUMN revalidation_required BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE pages ADD COLUMN revalidation_reason TEXT;
CREATE INDEX pages_revalidation_idx ON pages (revalidation_required) WHERE revalidation_required;
