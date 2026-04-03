"""Minimal Flask test server for integration tests.

Exposes:
  GET  /health                 — healthcheck
  POST /emit-test              — emits an SSE event via emit_event
  POST /api/trigger            — mock frontend trigger (captures events for verification)
  GET  /api/trigger/last-event — returns the last event received by the mock trigger
"""

import json

from flask import Flask, request, jsonify

from pamfilico_python_sse import emit_event

app = Flask(__name__)

# In-memory store for events received by the mock trigger
_last_event = {"eventName": None, "payload": None}


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


@app.route("/emit-test", methods=["POST"])
def emit_test():
    """Emit an SSE event. Body: {"event_name": "...", "payload": {...}}"""
    data = request.get_json() or {}
    event_name = data.get("event_name", "test_event")
    payload = data.get("payload", {"message": "hello"})
    success = emit_event(event_name, payload)
    return {"status": "emitted" if success else "failed", "event_name": event_name}


@app.route("/api/trigger", methods=["POST"])
def mock_trigger():
    """Mock of the Next.js /api/trigger endpoint. Stores events for test verification."""
    data = request.get_json() or {}
    _last_event["eventName"] = data.get("eventName")
    _last_event["payload"] = data.get("payload")
    return jsonify({"success": True, "eventName": data.get("eventName")})


@app.route("/api/trigger/last-event", methods=["GET"])
def last_event():
    """Return the last event received by the mock trigger."""
    return jsonify(_last_event)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
