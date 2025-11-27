from cli.views.contracts import get_contracts_menu_options


class DummyRole:
    def __init__(self, name):
        self.name = name


class DummyUser:
    def __init__(self, role_name):
        self.role = DummyRole(role_name)
        self.id = 1
        self.customers = []


class DummyPermService:
    def __init__(self, perms=None):
        self.perms = set(perms or [])

    def user_has_permission(self, user, perm_name):
        return perm_name in self.perms

    def can_create_contract(self, user):
        return 'contract:create' in self.perms


def labels(opts):
    return [label for label, _ in opts]


def test_management_sees_create_and_all():
    user = DummyUser('management')
    perm = DummyPermService(perms={'contract:read', 'contract:create'})
    opts = get_contracts_menu_options(user, perm)
    l = labels(opts)
    assert 'Afficher tous les contrats' in l
    assert 'Créer un contrat' in l


def test_sales_without_create_sees_read_only():
    user = DummyUser('sales')
    perm = DummyPermService(perms={'contract:read'})
    opts = get_contracts_menu_options(user, perm)
    l = labels(opts)
    assert 'Afficher tous les contrats' in l
    assert 'Créer un contrat' not in l
