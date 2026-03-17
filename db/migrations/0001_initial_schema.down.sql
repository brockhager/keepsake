PRAGMA foreign_keys = OFF;

BEGIN;

DROP INDEX IF EXISTS idx_audit_event_event_occurred;
DROP INDEX IF EXISTS idx_audit_event_entity_occurred;
DROP INDEX IF EXISTS idx_attachment_memory_revision;
DROP INDEX IF EXISTS idx_share_grant_person_granted;
DROP INDEX IF EXISTS idx_share_grant_active_per_pair;
DROP INDEX IF EXISTS idx_share_request_status_requested;
DROP INDEX IF EXISTS idx_share_request_memory_person_requested;
DROP INDEX IF EXISTS idx_memory_visibility_intent_person_created;
DROP INDEX IF EXISTS idx_memory_visibility_intent_memory_person;
DROP INDEX IF EXISTS idx_person_owner_display_name;
DROP INDEX IF EXISTS idx_memory_revision_created;
DROP INDEX IF EXISTS idx_memory_revision_memory_revision;
DROP INDEX IF EXISTS idx_memory_current_revision;
DROP INDEX IF EXISTS idx_memory_owner_created;

DROP TABLE IF EXISTS audit_event;
DROP TABLE IF EXISTS attachment;
DROP TABLE IF EXISTS share_grant;
DROP TABLE IF EXISTS share_request;
DROP TABLE IF EXISTS memory_visibility_intent;
DROP TABLE IF EXISTS person;
DROP TABLE IF EXISTS memory_revision;
DROP TABLE IF EXISTS memory;

COMMIT;

PRAGMA foreign_keys = ON;
