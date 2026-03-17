PRAGMA foreign_keys = ON;

BEGIN;

CREATE TABLE memory (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  archived_at TEXT,
  current_revision_id TEXT
);

CREATE TABLE memory_revision (
  id TEXT PRIMARY KEY,
  memory_id TEXT NOT NULL,
  revision_number INTEGER NOT NULL CHECK (revision_number > 0),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  author_type TEXT NOT NULL CHECK (author_type IN ('owner', 'ai_suggestion', 'import')),
  title TEXT NOT NULL DEFAULT '',
  body TEXT NOT NULL DEFAULT '',
  happened_at_start TEXT,
  happened_at_end TEXT,
  time_precision TEXT NOT NULL DEFAULT 'unknown' CHECK (time_precision IN ('exact', 'day', 'month', 'year', 'unknown')),
  certainty TEXT NOT NULL DEFAULT 'uncertain' CHECK (certainty IN ('certain', 'uncertain', 'speculative')),
  belief_context TEXT,
  edit_reason TEXT,
  supersedes_revision_id TEXT,
  FOREIGN KEY (memory_id) REFERENCES memory(id) ON DELETE RESTRICT,
  FOREIGN KEY (supersedes_revision_id) REFERENCES memory_revision(id) ON DELETE RESTRICT,
  UNIQUE (memory_id, revision_number)
);

CREATE TABLE person (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  display_name TEXT NOT NULL,
  contact_hint TEXT,
  notes_private TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  archived_at TEXT
);

CREATE TABLE memory_visibility_intent (
  id TEXT PRIMARY KEY,
  memory_id TEXT NOT NULL,
  person_id TEXT NOT NULL,
  source_revision_id TEXT NOT NULL,
  intent_type TEXT NOT NULL DEFAULT 'request_view' CHECK (intent_type = 'request_view'),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  canceled_at TEXT,
  FOREIGN KEY (memory_id) REFERENCES memory(id) ON DELETE RESTRICT,
  FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE RESTRICT,
  FOREIGN KEY (source_revision_id) REFERENCES memory_revision(id) ON DELETE RESTRICT
);

CREATE TABLE share_request (
  id TEXT PRIMARY KEY,
  memory_id TEXT NOT NULL,
  person_id TEXT NOT NULL,
  direction TEXT NOT NULL CHECK (direction IN ('owner_to_person', 'person_to_owner')),
  requested_by TEXT NOT NULL,
  requested_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  message TEXT,
  status TEXT NOT NULL CHECK (status IN ('pending', 'accepted', 'declined', 'canceled', 'expired')),
  decided_at TEXT,
  CHECK ((status = 'pending' AND decided_at IS NULL) OR (status <> 'pending' AND decided_at IS NOT NULL)),
  FOREIGN KEY (memory_id) REFERENCES memory(id) ON DELETE RESTRICT,
  FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE RESTRICT
);

CREATE TABLE share_grant (
  id TEXT PRIMARY KEY,
  memory_id TEXT NOT NULL,
  person_id TEXT NOT NULL,
  request_id TEXT NOT NULL,
  granted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  revoked_at TEXT,
  max_revision_id TEXT NOT NULL,
  max_revision_number INTEGER NOT NULL CHECK (max_revision_number > 0),
  CHECK (revoked_at IS NULL OR revoked_at >= granted_at),
  FOREIGN KEY (memory_id) REFERENCES memory(id) ON DELETE RESTRICT,
  FOREIGN KEY (person_id) REFERENCES person(id) ON DELETE RESTRICT,
  FOREIGN KEY (request_id) REFERENCES share_request(id) ON DELETE RESTRICT,
  FOREIGN KEY (max_revision_id) REFERENCES memory_revision(id) ON DELETE RESTRICT,
  UNIQUE (request_id)
);

CREATE TABLE attachment (
  id TEXT PRIMARY KEY,
  memory_revision_id TEXT NOT NULL,
  media_type TEXT NOT NULL,
  file_path TEXT NOT NULL,
  sha256 TEXT NOT NULL CHECK (length(sha256) = 64),
  captured_at TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  FOREIGN KEY (memory_revision_id) REFERENCES memory_revision(id) ON DELETE RESTRICT
);

CREATE TABLE audit_event (
  id TEXT PRIMARY KEY,
  occurred_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  actor_type TEXT NOT NULL CHECK (actor_type IN ('owner', 'person', 'system', 'ai')),
  actor_id TEXT,
  event_type TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(payload_json))
);

CREATE INDEX idx_memory_owner_created ON memory (owner_id, created_at DESC);
CREATE INDEX idx_memory_current_revision ON memory (current_revision_id);
CREATE INDEX idx_memory_revision_memory_revision ON memory_revision (memory_id, revision_number DESC);
CREATE INDEX idx_memory_revision_created ON memory_revision (created_at DESC);
CREATE INDEX idx_person_owner_display_name ON person (owner_id, display_name);
CREATE INDEX idx_memory_visibility_intent_memory_person ON memory_visibility_intent (memory_id, person_id);
CREATE INDEX idx_memory_visibility_intent_person_created ON memory_visibility_intent (person_id, created_at DESC);
CREATE INDEX idx_share_request_memory_person_requested ON share_request (memory_id, person_id, requested_at DESC);
CREATE INDEX idx_share_request_status_requested ON share_request (status, requested_at DESC);
CREATE UNIQUE INDEX idx_share_grant_active_per_pair ON share_grant (memory_id, person_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_share_grant_person_granted ON share_grant (person_id, granted_at DESC);
CREATE INDEX idx_attachment_memory_revision ON attachment (memory_revision_id);
CREATE INDEX idx_audit_event_entity_occurred ON audit_event (entity_type, entity_id, occurred_at DESC);
CREATE INDEX idx_audit_event_event_occurred ON audit_event (event_type, occurred_at DESC);

COMMIT;
