"""Emit SSE events to the frontend via POST to /api/trigger."""

import logging
import os
from typing import Any, Dict

import requests


def emit_event(event_name: str, payload: Dict[str, Any]) -> bool:
    """
    Emit an event to the frontend via SSE.

    POSTs {eventName, payload} to the Next.js /api/trigger endpoint,
    which broadcasts to all connected SSE clients.

    Args:
        event_name: Name of the event (e.g., "updated_favorite_123")
        payload: Dictionary of event data to send

    Returns:
        True if the event was sent successfully, False otherwise.

    Example:
        >>> emit_event("updated_favorite_123", {
        ...     "document_id": "123",
        ...     "is_favorite": True,
        ...     "updated_at": "2024-01-01T12:00:00"
        ... })
        True
    """
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
