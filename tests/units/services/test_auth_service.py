from unittest.mock import patch
from app.services.auth_service import AuthService
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace

def test_hash_and_verify_password_success():
    auth = AuthService()
    hashed = auth.hash_password("secret123")
    assert auth.verify_password(hashed, "secret123") is True

def test_verify_password_wrong_password_returns_false():
    auth = AuthService()
    hashed = auth.hash_password("secret123")
    assert auth.verify_password(hashed, "autre") is False

def test_verify_password_handles_exception(monkeypatch):
    auth = AuthService()
    class FakeHasher:
        def verify(self, *_):
            raise Exception("boom")
    monkeypatch.setattr(auth, "_ph", FakeHasher())
    assert auth.verify_password("hash", "password") is False

def test_create_token_passe_les_bons_parametres(monkeypatch):
    sentinel = "jwt-token"
    captured = {}
    def fake_encode(payload, secret, algorithm):
        captured["payload"] = payload
        captured["secret"] = secret
        captured["algorithm"] = algorithm
        return sentinel
    monkeypatch.setattr("app.services.auth_service.jwt.encode", fake_encode)
    token = AuthService().create_token(123)
    assert token == sentinel
    assert captured["payload"]["sub"] == "123"
    assert isinstance(captured["payload"]["iat"], datetime)
    assert captured["payload"]["exp"] > captured["payload"]["iat"]

def test_decode_token_retourne_le_payload(monkeypatch):
    sentinel_payload = {"sub": "99"}
    monkeypatch.setattr(
        "app.services.auth_service.jwt.decode",
        lambda token, secret, algorithms: sentinel_payload,
    )
    assert AuthService().decode_token("fake") is sentinel_payload