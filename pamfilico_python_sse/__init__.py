"""Pamfilico Python SSE - Server-Sent Events emitter for Flask backends."""

__version__ = "0.1.0"

from pamfilico_python_sse.emitter import emit_event
from pamfilico_python_sse.json_stream import (
    SSE_JSON_STREAM_HEADERS,
    encode_sse_json_data_line,
    iter_encode_sse_json_lines,
)

__all__ = [
    "emit_event",
    "SSE_JSON_STREAM_HEADERS",
    "encode_sse_json_data_line",
    "iter_encode_sse_json_lines",
]
