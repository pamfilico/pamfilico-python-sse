"""Integration tests for Redis emit path — require running Redis."""

import json
import os
import threading
import time

import pytest

REDIS_URL = os.environ.get("SSE_TEST_REDIS_URL", "redis://localhost:6399")


def _redis_available() -> bool:
    try:
        import redis
        r = redis.from_url(REDIS_URL)
        r.ping()
        return True
    except Exception:
        return False


redis_required = pytest.mark.skipif(
    not _redis_available(),
    reason="Redis required — run ./run-tests.sh or docker compose -f docker-compose.test.yml up",
)


@redis_required
def test_emit_publishes_to_redis_channel():
    """emit_event with REDIS_URL publishes to the correct Redis channel."""
    import redis as redis_lib
    import pamfilico_python_sse.emitter as emitter_mod

    # Reset cached client
    emitter_mod._redis_client = None

    subscriber = redis_lib.from_url(REDIS_URL)
    pubsub = subscriber.pubsub()
    pubsub.subscribe("testapp:sse_events")

    # Consume the subscribe confirmation message
    pubsub.get_message(timeout=2)

    received = []

    def listen():
        for msg in pubsub.listen():
            if msg["type"] == "message":
                received.append(json.loads(msg["data"]))
                break

    listener = threading.Thread(target=listen, daemon=True)
    listener.start()

    # Small delay to ensure subscriber is ready
    time.sleep(0.2)

    # Emit with Redis
    os.environ["REDIS_URL"] = REDIS_URL
    os.environ["APP_NAME"] = "testapp"
    try:
        from pamfilico_python_sse import emit_event
        result = emit_event("updated_favorite_99", {"document_id": "99", "is_favorite": True})
    finally:
        os.environ.pop("REDIS_URL", None)
        os.environ.pop("APP_NAME", None)
        emitter_mod._redis_client = None

    assert result is True

    listener.join(timeout=5)
    assert len(received) == 1
    assert received[0]["eventName"] == "updated_favorite_99"
    assert received[0]["payload"]["is_favorite"] is True

    pubsub.close()
    subscriber.close()


@redis_required
def test_emit_without_redis_url_uses_http():
    """Without REDIS_URL, emit_event does NOT touch Redis."""
    import redis as redis_lib
    import pamfilico_python_sse.emitter as emitter_mod

    emitter_mod._redis_client = None

    subscriber = redis_lib.from_url(REDIS_URL)
    pubsub = subscriber.pubsub()
    pubsub.subscribe("app:sse_events")
    pubsub.get_message(timeout=2)

    # Ensure REDIS_URL is not set
    os.environ.pop("REDIS_URL", None)

    from pamfilico_python_sse import emit_event
    # This will try HTTP and fail (no server), but should NOT publish to Redis
    emit_event("should_not_appear", {"test": True})

    time.sleep(0.5)
    msg = pubsub.get_message(timeout=1)
    assert msg is None or msg["type"] != "message"

    pubsub.close()
    subscriber.close()
