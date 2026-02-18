import pytest
import responses
import json
from unittest.mock import MagicMock, patch
import localgpt

def test_build_prompt():
    system_prompt = "You are a helper."
    turns = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]
    prompt = localgpt.build_prompt(system_prompt, turns)
    assert "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helper.<|eot_id|>" in prompt
    assert "<|start_header_id|>user<|end_header_id|>\n\nHello<|eot_id|>" in prompt
    assert "<|start_header_id|>assistant<|end_header_id|>\n\nHi there<|eot_id|>" in prompt
    assert prompt.endswith("<|start_header_id|>assistant<|end_header_id|>\n\n")

@responses.activate
def test_sse_stream_completion_success():
    # Mock the running server
    responses.add(
        responses.POST,
        "http://127.0.0.1:8080/completion",
        body="data: {\"content\": \"Hello\"}\n\ndata: {\"content\": \" World\"}\n\ndata: {\"stop\": true}\n\n",
        stream=True,
        status=200,
    )
    
    generator = localgpt.sse_stream_completion("test prompt")
    chunks = list(generator)
    assert chunks == ["Hello", " World"]

import requests

@responses.activate
def test_sse_stream_completion_retry():
    # Fail twice then succeed
    responses.add(
        responses.POST,
        "http://127.0.0.1:8080/completion",
        body=requests.exceptions.ConnectionError("Connection refused")
    )
    responses.add(
        responses.POST,
        "http://127.0.0.1:8080/completion",
        body=requests.exceptions.ConnectionError("Connection refused")
    )
    responses.add(
        responses.POST,
        "http://127.0.0.1:8080/completion",
        body="data: {\"content\": \"Success\"}\n\ndata: {\"stop\": true}\n\n",
        stream=True,
        status=200,
    )

    # We need to mock time.sleep to speed up test
    with patch("time.sleep"):
        generator = localgpt.sse_stream_completion("test prompt")
        chunks = list(generator)
    
    assert chunks == ["Success"]
    assert len(responses.calls) == 3

