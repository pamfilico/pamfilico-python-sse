"""Unit tests for emit_event — mocks the HTTP POST."""

from unittest.mock import patch, MagicMock

from pamfilico_python_sse import emit_event


class TestEmitEvent:
    @patch("pamfilico_python_sse.emitter.requests.post")
    def test_emit_event_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        result = emit_event("test_event", {"key": "value"})

        assert result is True
        mock_post.assert_called_once_with(
            "http://localhost:3000/api/trigger",
            json={"eventName": "test_event", "payload": {"key": "value"}},
            timeout=5,
        )

    @patch("pamfilico_python_sse.emitter.requests.post")
    def test_emit_event_failure_status(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_post.return_value = mock_resp

        result = emit_event("test_event", {"key": "value"})

        assert result is False

    @patch("pamfilico_python_sse.emitter.requests.post")
    def test_emit_event_connection_error(self, mock_post):
        import requests as req
        mock_post.side_effect = req.exceptions.ConnectionError("Connection refused")

        result = emit_event("test_event", {"key": "value"})

        assert result is False

    @patch("pamfilico_python_sse.emitter.requests.post")
    @patch.dict("os.environ", {"NEXTAUTH_URL": "http://frontend:3000"})
    def test_emit_event_custom_url(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        emit_event("hello", {"msg": "world"})

        mock_post.assert_called_once_with(
            "http://frontend:3000/api/trigger",
            json={"eventName": "hello", "payload": {"msg": "world"}},
            timeout=5,
        )

    @patch("pamfilico_python_sse.emitter.requests.post")
    def test_emit_event_timeout(self, mock_post):
        import requests as req
        mock_post.side_effect = req.exceptions.Timeout("Timeout")

        result = emit_event("test_event", {"key": "value"})

        assert result is False
