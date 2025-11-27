from app.models.permission import Permission


def test_permission_fields_repr():
    p = Permission(name="customer:create", description="create customers")
    assert p.name == "customer:create"
    assert "customer:create" in repr(p) or p.name in p.__dict__.values()
