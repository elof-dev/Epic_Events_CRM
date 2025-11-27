from app.services.auth_service import AuthService
import app.services.auth_service as auth_mod


def test_hash_and_verify_and_token(monkeypatch):
    a = AuthService()
    hashed = a.hash_password('secret')
    assert a.verify_password(hashed, 'secret')

    # ensure JWT secret exists for roundtrip
    monkeypatch.setattr(auth_mod, 'JWT_SECRET', 'testsecret')
    monkeypatch.setattr(auth_mod, 'JWT_ALGORITHM', 'HS256')
    monkeypatch.setattr(auth_mod, 'JWT_EXP_SECONDS', 60)
    token = a.create_token(123)
    payload = a.decode_token(token)
    assert str(payload['sub']) == '123'
