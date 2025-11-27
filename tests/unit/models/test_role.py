from app.models.role import Role


def test_role_repr_and_fields():
    r = Role(name="management", description="m")
    assert r.name == "management"
    assert "management" in repr(r)
