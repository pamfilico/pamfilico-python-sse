"""
SSE event definitions for {{ cookiecutter.project_name }}.

Define helper functions for each event your app emits.
This keeps event names and payloads consistent across routes.
"""

from datetime import datetime

from pamfilico_python_sse import emit_event


def emit_record_updated(entity: str, record_id: str, **extra) -> bool:
    """Emit a per-record update event.

    Example:
        emit_record_updated("favorite", document_id, is_favorite=True)
        # emits: updated_favorite_{document_id}
    """
    return emit_event(
        f"updated_{entity}_{record_id}",
        {
            f"{entity}_id": record_id,
            "updated_at": datetime.utcnow().isoformat(),
            **extra,
        },
    )


def emit_table_updated(entity: str, **extra) -> bool:
    """Emit a table-level refresh event.

    Example:
        emit_table_updated("favorites")
        # emits: updated_favorites_table
    """
    return emit_event(
        f"updated_{entity}_table",
        {"status": "ok", **extra},
    )
