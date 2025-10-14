import json
import logging

from kubemind_common.logging.setup import setup_logging, correlation_id_var


def test_json_logging_includes_correlation_id(capsys):
    setup_logging("INFO", "json")
    token = correlation_id_var.set("req-123")
    try:
        logging.getLogger("test").info("hello")
    finally:
        correlation_id_var.reset(token)
    captured = capsys.readouterr()
    data = (captured.out or captured.err).strip()
    payload = json.loads(data)
    assert payload["message"] == "hello"
    assert payload.get("correlation_id") == "req-123"
