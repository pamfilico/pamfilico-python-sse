"""Integration tests — require docker compose -f docker-compose.test.yml up.

Tests the real flow:
  1. POST /emit-test on Flask API (calls emit_event)
  2. emit_event POSTs to the same server's /api/trigger (mock frontend)
  3. Verify the event arrived at /api/trigger/last-event
"""

import os
import time

import pytest
import requests

API_URL = os.environ.get("SSE_TEST_API_URL", "http://localhost:5098")


def _api_available() -> bool:
    try:
        resp = requests.get(f"{API_URL}/health", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


integration_required = pytest.mark.skipif(
    not _api_available(),
    reason="API required — run ./run-tests.sh or docker compose -f docker-compose.test.yml up",
)


@integration_required
def test_emit_event_arrives_at_trigger():
    """Emit event via /emit-test, verify it was received by mock /api/trigger."""
    event_name = f"test_favorite_{int(time.time())}"
    payload = {"document_id": "abc-123", "is_favorite": True}

    resp = requests.post(
        f"{API_URL}/emit-test",
        json={"event_name": event_name, "payload": payload},
        timeout=5,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "emitted"

    # Verify the mock trigger received it
    last = requests.get(f"{API_URL}/api/trigger/last-event", timeout=5).json()
    assert last["eventName"] == event_name
    assert last["payload"]["document_id"] == "abc-123"
    assert last["payload"]["is_favorite"] is True


@integration_required
def test_emit_event_with_table_event():
    """Emit a table-level event (no entity ID)."""
    resp = requests.post(
        f"{API_URL}/emit-test",
        json={"event_name": "updated_favorites_table", "payload": {"status": "ok"}},
        timeout=5,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "emitted"

    last = requests.get(f"{API_URL}/api/trigger/last-event", timeout=5).json()
    assert last["eventName"] == "updated_favorites_table"
    assert last["payload"]["status"] == "ok"


@integration_required
def test_emit_event_complex_payload():
    """Emit event with a complex payload (nested values, timestamps)."""
    payload = {
        "contract_id": "xyz-456",
        "status": "completed",
        "signers": [
            {"email": "alice@example.com", "signed": True},
            {"email": "bob@example.com", "signed": True},
        ],
        "completed_at": "2024-06-15T14:30:00Z",
    }

    resp = requests.post(
        f"{API_URL}/emit-test",
        json={"event_name": "contract_updated_xyz-456", "payload": payload},
        timeout=5,
    )
    assert resp.status_code == 200

    last = requests.get(f"{API_URL}/api/trigger/last-event", timeout=5).json()
    assert last["eventName"] == "contract_updated_xyz-456"
    assert last["payload"]["status"] == "completed"
    assert len(last["payload"]["signers"]) == 2
