PRAGMA foreign_keys = ON;

BEGIN;

CREATE TRIGGER trg_memory_insert_current_revision_null
BEFORE INSERT ON memory
WHEN NEW.current_revision_id IS NOT NULL
BEGIN
  SELECT RAISE(ABORT, 'current_revision_id must be NULL when creating memory');
END;

CREATE TRIGGER trg_memory_update_current_revision_valid
BEFORE UPDATE OF current_revision_id ON memory
WHEN NEW.current_revision_id IS NOT NULL
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1
      FROM memory_revision mr
      WHERE mr.id = NEW.current_revision_id
        AND mr.memory_id = NEW.id
    ) THEN RAISE(ABORT, 'current_revision_id must reference a revision of the same memory')
  END;
END;

CREATE TRIGGER trg_memory_clear_current_revision_blocked
BEFORE UPDATE OF current_revision_id ON memory
WHEN OLD.current_revision_id IS NOT NULL AND NEW.current_revision_id IS NULL
BEGIN
  SELECT RAISE(ABORT, 'current_revision_id cannot be cleared once set');
END;

CREATE TRIGGER trg_memory_revision_supersedes_same_memory
BEFORE INSERT ON memory_revision
WHEN NEW.supersedes_revision_id IS NOT NULL
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1
      FROM memory_revision prior
      WHERE prior.id = NEW.supersedes_revision_id
        AND prior.memory_id = NEW.memory_id
    ) THEN RAISE(ABORT, 'supersedes_revision_id must reference a revision in the same memory')
  END;
END;

CREATE TRIGGER trg_memory_revision_supersedes_forward_only
BEFORE INSERT ON memory_revision
WHEN NEW.supersedes_revision_id IS NOT NULL
BEGIN
  SELECT CASE
    WHEN NEW.revision_number <= (
      SELECT prior.revision_number
      FROM memory_revision prior
      WHERE prior.id = NEW.supersedes_revision_id
    ) THEN RAISE(ABORT, 'revision_number must increase when superseding')
  END;
END;

CREATE TRIGGER trg_memory_revision_first_has_no_supersede
BEFORE INSERT ON memory_revision
WHEN NEW.revision_number = 1 AND NEW.supersedes_revision_id IS NOT NULL
BEGIN
  SELECT RAISE(ABORT, 'first revision cannot supersede another revision');
END;

CREATE TRIGGER trg_memory_revision_nonfirst_requires_supersede
BEFORE INSERT ON memory_revision
WHEN NEW.revision_number > 1 AND NEW.supersedes_revision_id IS NULL
BEGIN
  SELECT RAISE(ABORT, 'non-first revision must set supersedes_revision_id');
END;

CREATE TRIGGER trg_memory_revision_immutable_update
BEFORE UPDATE ON memory_revision
BEGIN
  SELECT RAISE(ABORT, 'memory_revision is append-only and cannot be updated');
END;

CREATE TRIGGER trg_memory_revision_immutable_delete
BEFORE DELETE ON memory_revision
BEGIN
  SELECT RAISE(ABORT, 'memory_revision is append-only and cannot be deleted');
END;

CREATE TRIGGER trg_visibility_intent_source_matches_memory_insert
BEFORE INSERT ON memory_visibility_intent
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1
      FROM memory_revision mr
      WHERE mr.id = NEW.source_revision_id
        AND mr.memory_id = NEW.memory_id
    ) THEN RAISE(ABORT, 'source_revision_id must reference a revision in the same memory')
  END;
END;

CREATE TRIGGER trg_visibility_intent_source_matches_memory_update
BEFORE UPDATE OF memory_id, source_revision_id ON memory_visibility_intent
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1
      FROM memory_revision mr
      WHERE mr.id = NEW.source_revision_id
        AND mr.memory_id = NEW.memory_id
    ) THEN RAISE(ABORT, 'source_revision_id must reference a revision in the same memory')
  END;
END;

CREATE TRIGGER trg_share_request_identity_immutable
BEFORE UPDATE ON share_request
WHEN NEW.memory_id IS NOT OLD.memory_id
  OR NEW.person_id IS NOT OLD.person_id
  OR NEW.direction IS NOT OLD.direction
  OR NEW.requested_by IS NOT OLD.requested_by
  OR NEW.requested_at IS NOT OLD.requested_at
BEGIN
  SELECT RAISE(ABORT, 'share_request identity fields are immutable');
END;

CREATE TRIGGER trg_share_request_terminal_status_locked
BEFORE UPDATE OF status ON share_request
WHEN OLD.status <> 'pending' AND NEW.status <> OLD.status
BEGIN
  SELECT RAISE(ABORT, 'share_request terminal status cannot change');
END;

CREATE TRIGGER trg_share_grant_request_must_match_accepted
BEFORE INSERT ON share_grant
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1
      FROM share_request sr
      WHERE sr.id = NEW.request_id
        AND sr.status = 'accepted'
        AND sr.memory_id = NEW.memory_id
        AND sr.person_id = NEW.person_id
    ) THEN RAISE(ABORT, 'share_grant requires accepted request with matching memory and person')
  END;
END;

CREATE TRIGGER trg_share_grant_revision_bound_valid
BEFORE INSERT ON share_grant
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1
      FROM memory_revision mr
      WHERE mr.id = NEW.max_revision_id
        AND mr.memory_id = NEW.memory_id
        AND mr.revision_number = NEW.max_revision_number
    ) THEN RAISE(ABORT, 'share_grant max revision must match memory and revision number')
  END;
END;

CREATE TRIGGER trg_share_grant_core_immutable
BEFORE UPDATE ON share_grant
WHEN NEW.memory_id IS NOT OLD.memory_id
  OR NEW.person_id IS NOT OLD.person_id
  OR NEW.request_id IS NOT OLD.request_id
  OR NEW.granted_at IS NOT OLD.granted_at
  OR NEW.max_revision_id IS NOT OLD.max_revision_id
  OR NEW.max_revision_number IS NOT OLD.max_revision_number
BEGIN
  SELECT RAISE(ABORT, 'share_grant core fields are immutable');
END;

CREATE TRIGGER trg_share_grant_revocation_once
BEFORE UPDATE OF revoked_at ON share_grant
WHEN OLD.revoked_at IS NOT NULL AND NEW.revoked_at IS NOT OLD.revoked_at
BEGIN
  SELECT RAISE(ABORT, 'share_grant revoked_at is immutable once set');
END;

CREATE TRIGGER trg_audit_event_immutable_update
BEFORE UPDATE ON audit_event
BEGIN
  SELECT RAISE(ABORT, 'audit_event is append-only and cannot be updated');
END;

CREATE TRIGGER trg_audit_event_immutable_delete
BEFORE DELETE ON audit_event
BEGIN
  SELECT RAISE(ABORT, 'audit_event is append-only and cannot be deleted');
END;

CREATE VIEW memory_current_view AS
SELECT
  m.id AS memory_id,
  m.owner_id,
  m.created_at AS memory_created_at,
  m.archived_at AS memory_archived_at,
  m.current_revision_id,
  mr.revision_number AS current_revision_number,
  mr.created_at AS current_revision_created_at,
  mr.title AS current_title,
  mr.certainty AS current_certainty,
  (
    SELECT COUNT(*)
    FROM share_grant sg
    WHERE sg.memory_id = m.id
      AND sg.revoked_at IS NULL
  ) AS active_share_count
FROM memory m
LEFT JOIN memory_revision mr ON mr.id = m.current_revision_id;

CREATE VIEW memory_history_view AS
SELECT
  mr.id AS revision_id,
  mr.memory_id,
  mr.revision_number,
  mr.created_at,
  mr.author_type,
  mr.title,
  mr.body,
  mr.happened_at_start,
  mr.happened_at_end,
  mr.time_precision,
  mr.certainty,
  mr.belief_context,
  mr.edit_reason,
  mr.supersedes_revision_id
FROM memory_revision mr;

CREATE VIEW person_shares_view AS
SELECT
  sg.person_id,
  p.display_name,
  sg.memory_id,
  sg.granted_at,
  sg.revoked_at,
  sg.max_revision_id,
  sg.max_revision_number,
  mr.title AS max_revision_title,
  mr.created_at AS max_revision_created_at
FROM share_grant sg
JOIN person p ON p.id = sg.person_id
JOIN memory_revision mr ON mr.id = sg.max_revision_id;

COMMIT;
