from kubemind_common.security.auth import parse_bearer, parse_basic
from kubemind_common.security.hmac import compute_hmac_sha256, verify_hmac_sha256
from kubemind_common.security.jwt import create_jwt, verify_jwt


def test_parse_bearer():
    assert parse_bearer("Bearer abc") == "abc"
    assert parse_bearer("bearer token") == "token"
    assert parse_bearer(None) is None


def test_parse_basic():
    import base64

    creds = base64.b64encode(b"user:pass").decode()
    assert parse_basic(f"Basic {creds}") == ("user", "pass")
    assert parse_basic(None) is None


def test_hmac_verify():
    secret = "s3cr3t"
    body = b"payload"
    signature = compute_hmac_sha256(secret, body)
    assert verify_hmac_sha256(secret, body, signature)
    assert not verify_hmac_sha256(secret, b"other", signature)


def test_jwt_roundtrip():
    token = create_jwt({"sub": "user1"}, secret="secret", expires_in=60)
    claims = verify_jwt(token, secret="secret")
    assert claims["sub"] == "user1"

