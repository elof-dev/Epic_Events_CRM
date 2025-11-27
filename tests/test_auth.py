from app.services.auth_service import AuthService


def test_hash_and_verify():
    auth = AuthService()
    pw = "secret-password"
    h = auth.hash_password(pw)
    assert auth.verify_password(h, pw)
