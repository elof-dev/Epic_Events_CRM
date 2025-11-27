from cli.views.events import get_event_menu_options


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
        # perms: set of permission strings
        self.perms = set(perms or [])

    def user_has_permission(self, user, perm_name):
        return perm_name in self.perms


def labels(opts):
    return [label for label, _ in opts]


def test_sales_with_create_and_read_sees_create_and_all():
    user = DummyUser('sales')
    perm = DummyPermService(perms={'event:create', 'event:read'})
    opts = get_event_menu_options(user, perm)
    l = labels(opts)
    assert 'Afficher tous les évènements' in l
    assert 'Créer un évènement' in l
    assert 'Mes évènements' not in l
    assert 'Evènements sans support assigned' not in l


def test_support_sees_mine_and_all_only_with_read():
    user = DummyUser('support')
    perm = DummyPermService(perms={'event:read'})
    opts = get_event_menu_options(user, perm)
    l = labels(opts)
    assert 'Afficher tous les évènements' in l
    assert 'Mes évènements' in l
    assert 'Créer un évènement' not in l
    assert 'Evènements sans support assigned' not in l


def test_management_sees_nosupport_with_read():
    user = DummyUser('management')
    perm = DummyPermService(perms={'event:read'})
    opts = get_event_menu_options(user, perm)
    l = labels(opts)
    assert 'Afficher tous les évènements' in l
    assert 'Evènements sans support assigned' in l
    assert 'Créer un évènement' not in l
    assert 'Mes évènements' not in l
