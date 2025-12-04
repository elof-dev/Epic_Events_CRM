from types import SimpleNamespace

from cli import crm_interface


def _setup_token(tmp_path, monkeypatch):
    token_path = tmp_path / "token.jwt"
    monkeypatch.setattr(crm_interface, "_TOKEN_FILE", token_path)
    return token_path


def test_token_file_round_trip(tmp_path, monkeypatch):
    token_path = _setup_token(tmp_path, monkeypatch)

    crm_interface._write_token("  jeton   ")

    assert token_path.read_text(encoding="utf-8") == "jeton"
    assert crm_interface._read_token() == "jeton"

    crm_interface._clear_token()
    assert not token_path.exists()


def test_user_from_token_returns_user(tmp_path, monkeypatch):
    _setup_token(tmp_path, monkeypatch)
    crm_interface._write_token("valid-token")

    auth = SimpleNamespace(decode_token=lambda token: {"sub": "7"})
    user = SimpleNamespace(id=7)

    class DummySession:
        def get(self, model, object_id):
            assert model is crm_interface.User
            return user if object_id == 7 else None

    retrieved = crm_interface._user_from_token(DummySession(), auth)
    assert retrieved is user


def test_user_from_token_with_invalid_token_clears_file(tmp_path, monkeypatch):
    token_path = _setup_token(tmp_path, monkeypatch)
    crm_interface._write_token("bad-token")

    class DummyAuth:
        def decode_token(self, token):
            raise ValueError("boom")

    class DummySession:
        def get(self, model, object_id):  # pragma: no cover - ne doit pas etre appele
            raise AssertionError("get ne doit pas etre invoque pour un token invalide")

    assert crm_interface._user_from_token(DummySession(), DummyAuth()) is None
    assert not token_path.exists()


def test_user_from_token_with_unknown_user_clears_file(tmp_path, monkeypatch):
    token_path = _setup_token(tmp_path, monkeypatch)
    crm_interface._write_token("orphan-token")

    auth = SimpleNamespace(decode_token=lambda token: {"sub": "42"})

    class DummySession:
        def get(self, model, object_id):
            assert model is crm_interface.User
            return None

    assert crm_interface._user_from_token(DummySession(), auth) is None
    assert not token_path.exists()
