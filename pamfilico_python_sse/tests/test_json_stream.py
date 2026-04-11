"""Tests for JSON-in-SSE line encoding (Flask long-poll / stream responses)."""

import json

import pytest

from pamfilico_python_sse.json_stream import (
    SSE_JSON_STREAM_HEADERS,
    encode_sse_json_data_line,
    iter_encode_sse_json_lines,
)


def test_encode_sse_json_data_line_format() -> None:
    payload = {"event": "progress", "step_index": 1}
    line = encode_sse_json_data_line(payload)
    assert line.startswith("data: ")
    assert line.endswith("\n\n")
    json_str = line.removeprefix("data: ").removesuffix("\n\n")
    assert json.loads(json_str) == payload


def test_encode_non_ascii_round_trip() -> None:
    payload = {"message": "café 日本語"}
    line = encode_sse_json_data_line(payload)
    json_str = line.removeprefix("data: ").removesuffix("\n\n")
    assert json.loads(json_str) == payload


def test_iter_encode_sse_json_lines() -> None:
    items = [{"a": 1}, {"b": 2}]

    def gen():
        yield from items

    lines = list(iter_encode_sse_json_lines(gen()))
    assert len(lines) == 2
    for i, line in enumerate(lines):
        assert line.startswith("data: ")
        assert line.endswith("\n\n")
        body = json.loads(line.removeprefix("data: ").removesuffix("\n\n"))
        assert body == items[i]


def test_sse_json_stream_headers_keys() -> None:
    assert "Cache-Control" in SSE_JSON_STREAM_HEADERS
    assert SSE_JSON_STREAM_HEADERS["Cache-Control"] == "no-cache"
