from app.models.user import User


def test_user_repr_and_fields():
    u = User(user_first_name="A", user_last_name="B", email="a@b.com", phone_number=None, username="u1", password_hash="x", role_id=1)
    r = repr(u)
    assert "u1" in r
    assert u.user_first_name == "A"
