PRAGMA foreign_keys = ON;

BEGIN;

DROP VIEW IF EXISTS person_shares_view;
DROP VIEW IF EXISTS memory_history_view;
DROP VIEW IF EXISTS memory_current_view;

DROP TRIGGER IF EXISTS trg_audit_event_immutable_delete;
DROP TRIGGER IF EXISTS trg_audit_event_immutable_update;
DROP TRIGGER IF EXISTS trg_share_grant_revocation_once;
DROP TRIGGER IF EXISTS trg_share_grant_core_immutable;
DROP TRIGGER IF EXISTS trg_share_grant_revision_bound_valid;
DROP TRIGGER IF EXISTS trg_share_grant_request_must_match_accepted;
DROP TRIGGER IF EXISTS trg_share_request_terminal_status_locked;
DROP TRIGGER IF EXISTS trg_share_request_identity_immutable;
DROP TRIGGER IF EXISTS trg_visibility_intent_source_matches_memory_update;
DROP TRIGGER IF EXISTS trg_visibility_intent_source_matches_memory_insert;
DROP TRIGGER IF EXISTS trg_memory_revision_immutable_delete;
DROP TRIGGER IF EXISTS trg_memory_revision_immutable_update;
DROP TRIGGER IF EXISTS trg_memory_revision_nonfirst_requires_supersede;
DROP TRIGGER IF EXISTS trg_memory_revision_first_has_no_supersede;
DROP TRIGGER IF EXISTS trg_memory_revision_supersedes_forward_only;
DROP TRIGGER IF EXISTS trg_memory_revision_supersedes_same_memory;
DROP TRIGGER IF EXISTS trg_memory_clear_current_revision_blocked;
DROP TRIGGER IF EXISTS trg_memory_update_current_revision_valid;
DROP TRIGGER IF EXISTS trg_memory_insert_current_revision_null;

COMMIT;
