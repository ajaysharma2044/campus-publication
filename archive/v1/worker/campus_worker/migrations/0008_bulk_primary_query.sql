-- 0008: the short searchable query each bulk question's title must carry (hub pages and entity guides have natural primary queries, not their full question text)
ALTER TABLE bulk_questions ADD COLUMN IF NOT EXISTS primary_query TEXT;
