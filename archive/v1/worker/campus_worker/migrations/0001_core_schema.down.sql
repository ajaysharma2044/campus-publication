-- Down for 0001_core_schema. DESTRUCTIVE: drops every table. Only valid on empty/dev databases.
-- Production recovery approach: restore from backup (scripts/restore_test.sh), never run this.
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
