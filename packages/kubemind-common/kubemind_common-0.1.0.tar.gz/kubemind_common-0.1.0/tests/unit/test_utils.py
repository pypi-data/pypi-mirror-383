from kubemind_common.utils.json import dumps_redacted
from kubemind_common.http.client import create_http_client


def test_dumps_redacted():
    data = {"token": "abc", "nested": {"password": "secret", "ok": True}}
    s = dumps_redacted(data)
    assert "<redacted>" in s
    assert "secret" not in s


def test_http_client_ua():
    client = create_http_client()
    assert client.headers["User-Agent"].startswith("kubemind")

