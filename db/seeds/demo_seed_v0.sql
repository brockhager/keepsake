PRAGMA foreign_keys = ON;

BEGIN;

INSERT INTO vault (id, owner_id, name, is_default)
VALUES
  ('demo-vault-1', 'demo-owner', 'Family History', 1),
  ('demo-vault-2', 'demo-owner', 'Private Reflections', 0);

INSERT INTO person (id, owner_id, display_name, contact_hint, notes_private)
VALUES
  ('demo-person-1', 'demo-owner', 'Jordan Vale', 'jordan.demo@example.invalid', 'Synthetic person for demo only.'),
  ('demo-person-2', 'demo-owner', 'Riley North', 'riley.demo@example.invalid', 'Synthetic person for demo only.');

INSERT INTO memory (id, owner_id, vault_id, archived_at, current_revision_id)
VALUES
  ('demo-memory-1', 'demo-owner', 'demo-vault-1', NULL, NULL),
  ('demo-memory-2', 'demo-owner', 'demo-vault-2', NULL, NULL);

INSERT INTO memory_revision (
  id,
  memory_id,
  revision_number,
  author_type,
  title,
  body,
  happened_at_start,
  happened_at_end,
  time_precision,
  certainty,
  belief_context,
  edit_reason,
  supersedes_revision_id
)
VALUES
  (
    'demo-rev-1',
    'demo-memory-1',
    1,
    'owner',
    'First week in the new apartment',
    'Everything felt temporary that week. Future me: this entry is synthetic demo data.',
    '2025-05-01T00:00:00.000Z',
    NULL,
    'day',
    'uncertain',
    'I thought the move would feel final quickly, but it did not.',
    'Initial capture',
    NULL
  ),
  (
    'demo-rev-2',
    'demo-memory-1',
    2,
    'owner',
    'First week in the new apartment',
    'Two months later, I remember the same week as calmer than it felt in real time. Synthetic demo data.',
    '2025-05-01T00:00:00.000Z',
    NULL,
    'day',
    'uncertain',
    'My original stress memory softened over time.',
    'Added context after reflection',
    'demo-rev-1'
  ),
  (
    'demo-rev-3',
    'demo-memory-2',
    1,
    'import',
    'Voice note from night walk',
    'Imported transcript: wind, traffic, and a clear thought about slowing down. Synthetic demo data.',
    '2024-11-14T21:00:00.000Z',
    NULL,
    'exact',
    'speculative',
    'Unsure if this happened exactly this way; recording uncertainty matters.',
    'Imported from mock voice note',
    NULL
  );

UPDATE memory
SET current_revision_id = 'demo-rev-2'
WHERE id = 'demo-memory-1';

UPDATE memory
SET current_revision_id = 'demo-rev-3'
WHERE id = 'demo-memory-2';

INSERT INTO memory_visibility_intent (id, memory_id, person_id, source_revision_id, intent_type)
VALUES
  ('demo-intent-1', 'demo-memory-1', 'demo-person-1', 'demo-rev-2', 'request_view'),
  ('demo-intent-2', 'demo-memory-2', 'demo-person-2', 'demo-rev-3', 'request_view');

INSERT INTO share_request (
  id,
  memory_id,
  person_id,
  direction,
  requested_by,
  requested_at,
  message,
  status,
  decided_at
)
VALUES
  (
    'demo-request-1',
    'demo-memory-1',
    'demo-person-1',
    'owner_to_person',
    'demo-owner',
    '2026-01-05T10:00:00.000Z',
    'Synthetic request used to demonstrate explicit sharing flow.',
    'accepted',
    '2026-01-06T09:00:00.000Z'
  ),
  (
    'demo-request-2',
    'demo-memory-2',
    'demo-person-2',
    'owner_to_person',
    'demo-owner',
    '2026-01-07T12:00:00.000Z',
    'Synthetic pending request used to demonstrate non-shared state.',
    'pending',
    NULL
  );

INSERT INTO share_grant (
  id,
  memory_id,
  person_id,
  request_id,
  granted_at,
  revoked_at,
  max_revision_id,
  max_revision_number
)
VALUES
  (
    'demo-grant-1',
    'demo-memory-1',
    'demo-person-1',
    'demo-request-1',
    '2026-01-06T09:00:00.000Z',
    NULL,
    'demo-rev-2',
    2
  );

INSERT INTO attachment (
  id,
  memory_revision_id,
  media_type,
  file_path,
  sha256,
  captured_at
)
VALUES
  (
    'demo-attachment-1',
    'demo-rev-3',
    'audio/m4a',
    'demo/audio/night-walk.m4a',
    '1111111111111111111111111111111111111111111111111111111111111111',
    '2024-11-14T21:00:00.000Z'
  );

INSERT INTO audit_event (
  id,
  occurred_at,
  actor_type,
  actor_id,
  event_type,
  entity_type,
  entity_id,
  payload_json
)
VALUES
  (
    'demo-audit-1',
    '2026-01-05T10:00:00.000Z',
    'owner',
    'demo-owner',
    'memory.created',
    'memory',
    'demo-memory-1',
    '{"synthetic":true,"source":"demo_seed_v0"}'
  ),
  (
    'demo-audit-2',
    '2026-01-06T09:00:00.000Z',
    'owner',
    'demo-owner',
    'share.accepted',
    'share_request',
    'demo-request-1',
    '{"synthetic":true,"source":"demo_seed_v0"}'
  ),
  (
    'demo-audit-3',
    '2026-01-07T12:00:00.000Z',
    'owner',
    'demo-owner',
    'share.requested',
    'share_request',
    'demo-request-2',
    '{"synthetic":true,"source":"demo_seed_v0"}'
  );

COMMIT;
