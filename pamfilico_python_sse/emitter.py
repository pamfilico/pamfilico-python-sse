"""Emit SSE events to the frontend via HTTP POST or Redis pub/sub."""

import json
import logging
import os
from typing import Any, Dict

import requests

_redis_client = None


def _get_redis_client():
    """Lazily create and cache a Redis client from REDIS_URL."""
    global _redis_client
    if _redis_client is None:
        import redis as redis_lib

        _redis_client = redis_lib.from_url(os.getenv("REDIS_URL", ""))
    return _redis_client


def _get_channel() -> str:
    """Build the Redis channel name: {APP_NAME}:{SSE_CHANNEL}."""
    app_name = os.getenv("APP_NAME", "app")
    sse_channel = os.getenv("SSE_CHANNEL", "sse_events")
    return f"{app_name}:{sse_channel}"


def _emit_via_redis(event_name: str, payload: Dict[str, Any]) -> bool:
    """Publish event to Redis channel."""
    channel = _get_channel()
    message = json.dumps({"eventName": event_name, "payload": payload})
    try:
        client = _get_redis_client()
        client.publish(channel, message)
        logging.info(
            f"Event '{event_name}' published to Redis channel '{channel}'"
        )
        return True
    except Exception as e:
        logging.error(f"Redis publish error for '{event_name}': {e}")
        return False


def _emit_via_http(event_name: str, payload: Dict[str, Any]) -> bool:
    """POST event to the Next.js /api/trigger endpoint."""
    frontend_url = os.getenv("NEXTAUTH_URL", "http://localhost:3000")
    trigger_endpoint = f"{frontend_url}/api/trigger"

    try:
        response = requests.post(
            trigger_endpoint,
            json={"eventName": event_name, "payload": payload},
            timeout=5,
        )

        if response.status_code == 200:
            logging.info(
                f"Event '{event_name}' emitted successfully. Payload: {payload}"
            )
            return True
        else:
            logging.error(
                f"Failed to emit event '{event_name}'. "
                f"Status {response.status_code}: {response.text}"
            )
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Error emitting event '{event_name}': {e}")
        return False


def emit_event(event_name: str, payload: Dict[str, Any]) -> bool:
    """
    Emit an event to the frontend via SSE.

    If REDIS_URL is set, publishes to a Redis channel.
    Otherwise, POSTs to the Next.js /api/trigger endpoint.

    Args:
        event_name: Name of the event (e.g., "updated_favorite_123")
        payload: Dictionary of event data to send

    Returns:
        True if the event was sent successfully, False otherwise.

    Environment variables:
        REDIS_URL: If set, uses Redis pub/sub instead of HTTP POST
        APP_NAME: Redis channel prefix (default: "app")
        SSE_CHANNEL: Redis channel suffix (default: "sse_events")
        NEXTAUTH_URL: Frontend URL for HTTP mode (default: "http://localhost:3000")
    """
    if os.getenv("REDIS_URL"):
        return _emit_via_redis(event_name, payload)
    return _emit_via_http(event_name, payload)
