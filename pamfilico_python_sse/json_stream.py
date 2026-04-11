"""
SSE framing for JSON payloads in long-lived HTTP responses (encode only).

Pairs with Next.js clients that parse ``data: {...}\\n\\n`` lines (see @pamfilico/nextjs-sse).
Callers own dict contents (steps, percents, etc.).
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, Mapping, Union

JsonDict = Dict[str, Any]

SSE_JSON_STREAM_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def encode_sse_json_data_line(payload: Union[JsonDict, Mapping[str, Any]]) -> str:
    """Format one SSE event body as a single JSON object (``data: ...\\n\\n``)."""
    return f"data: {json.dumps(payload)}\n\n"


def iter_encode_sse_json_lines(payloads: Iterator[JsonDict]) -> Iterator[str]:
    for item in payloads:
        yield encode_sse_json_data_line(item)
