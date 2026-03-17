PRAGMA foreign_keys = ON;

BEGIN;

CREATE TABLE vault (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  is_default INTEGER NOT NULL DEFAULT 0 CHECK (is_default IN (0, 1))
);

CREATE INDEX idx_vault_owner_name ON vault (owner_id, name);
CREATE UNIQUE INDEX idx_vault_owner_default ON vault (owner_id) WHERE is_default = 1;

ALTER TABLE memory ADD COLUMN vault_id TEXT REFERENCES vault(id) ON DELETE RESTRICT;

INSERT INTO vault (id, owner_id, name, is_default)
SELECT 'vault-default:' || owners.owner_id, owners.owner_id, 'Default Vault', 1
FROM (
  SELECT DISTINCT owner_id
  FROM memory
  WHERE vault_id IS NULL
) AS owners
WHERE NOT EXISTS (
  SELECT 1
  FROM vault v
  WHERE v.id = 'vault-default:' || owners.owner_id
);

UPDATE memory
SET vault_id = 'vault-default:' || owner_id
WHERE vault_id IS NULL;

CREATE INDEX idx_memory_vault_created ON memory (vault_id, created_at DESC);

CREATE TRIGGER trg_memory_vault_required_insert
BEFORE INSERT ON memory
WHEN NEW.vault_id IS NULL
BEGIN
  SELECT RAISE(ABORT, 'memory must belong to a vault');
END;

CREATE TRIGGER trg_memory_vault_required_update
BEFORE UPDATE OF vault_id ON memory
WHEN NEW.vault_id IS NULL
BEGIN
  SELECT RAISE(ABORT, 'memory must belong to a vault');
END;

CREATE TRIGGER trg_memory_vault_owner_match_insert
BEFORE INSERT ON memory
WHEN NEW.vault_id IS NOT NULL
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1
      FROM vault v
      WHERE v.id = NEW.vault_id
        AND v.owner_id = NEW.owner_id
    ) THEN RAISE(ABORT, 'memory vault must exist and belong to the same owner')
  END;
END;

CREATE TRIGGER trg_memory_vault_owner_match_update
BEFORE UPDATE OF vault_id, owner_id ON memory
WHEN NEW.vault_id IS NOT NULL
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (
      SELECT 1
      FROM vault v
      WHERE v.id = NEW.vault_id
        AND v.owner_id = NEW.owner_id
    ) THEN RAISE(ABORT, 'memory vault must exist and belong to the same owner')
  END;
END;

DROP VIEW IF EXISTS memory_current_view;

CREATE VIEW memory_current_view AS
SELECT
  m.id AS memory_id,
  m.owner_id,
  m.vault_id,
  v.name AS vault_name,
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
LEFT JOIN vault v ON v.id = m.vault_id
LEFT JOIN memory_revision mr ON mr.id = m.current_revision_id;

COMMIT;
