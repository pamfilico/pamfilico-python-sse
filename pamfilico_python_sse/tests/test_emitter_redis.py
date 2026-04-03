"""Unit tests for Redis emit path — mocks the Redis client."""

import json
from unittest.mock import patch, MagicMock

import pamfilico_python_sse.emitter as emitter_mod
from pamfilico_python_sse import emit_event


class TestEmitEventRedis:
    def setup_method(self):
        # Reset cached client between tests
        emitter_mod._redis_client = None

    @patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379"})
    @patch("pamfilico_python_sse.emitter._get_redis_client")
    def test_emit_uses_redis_when_url_set(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = emit_event("test_event", {"key": "value"})

        assert result is True
        mock_client.publish.assert_called_once()
        channel, message = mock_client.publish.call_args[0]
        assert channel == "app:sse_events"
        parsed = json.loads(message)
        assert parsed["eventName"] == "test_event"
        assert parsed["payload"]["key"] == "value"

    @patch.dict("os.environ", {}, clear=True)
    @patch("pamfilico_python_sse.emitter.requests.post")
    def test_emit_uses_http_when_no_redis_url(self, mock_post):
        # Ensure REDIS_URL is not set
        import os
        os.environ.pop("REDIS_URL", None)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        result = emit_event("test_event", {"key": "value"})

        assert result is True
        mock_post.assert_called_once()

    @patch.dict("os.environ", {
        "REDIS_URL": "redis://localhost:6379",
        "APP_NAME": "myapp",
        "SSE_CHANNEL": "custom",
    })
    @patch("pamfilico_python_sse.emitter._get_redis_client")
    def test_emit_redis_custom_channel(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        emit_event("hello", {"msg": "world"})

        channel, _ = mock_client.publish.call_args[0]
        assert channel == "myapp:custom"

    @patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379"})
    @patch("pamfilico_python_sse.emitter._get_redis_client")
    def test_emit_redis_connection_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.publish.side_effect = Exception("Connection refused")
        mock_get_client.return_value = mock_client

        result = emit_event("test_event", {"key": "value"})

        assert result is False

    @patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379"})
    @patch("pamfilico_python_sse.emitter._get_redis_client")
    def test_emit_redis_payload_is_json(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        emit_event("updated_favorite_123", {
            "document_id": "123",
            "is_favorite": True,
            "updated_at": "2024-01-01T12:00:00",
        })

        _, message = mock_client.publish.call_args[0]
        parsed = json.loads(message)
        assert parsed["eventName"] == "updated_favorite_123"
        assert parsed["payload"]["is_favorite"] is True
