PRAGMA foreign_keys = ON;

BEGIN;

DROP VIEW IF EXISTS memory_current_view;

DROP TRIGGER IF EXISTS trg_memory_vault_owner_match_update;
DROP TRIGGER IF EXISTS trg_memory_vault_owner_match_insert;
DROP TRIGGER IF EXISTS trg_memory_vault_required_update;
DROP TRIGGER IF EXISTS trg_memory_vault_required_insert;

DROP INDEX IF EXISTS idx_memory_vault_created;
DROP INDEX IF EXISTS idx_vault_owner_default;
DROP INDEX IF EXISTS idx_vault_owner_name;

ALTER TABLE memory DROP COLUMN vault_id;

DROP TABLE IF EXISTS vault;

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

COMMIT;
