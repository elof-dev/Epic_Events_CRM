from click.testing import CliRunner
import click
from cli.views.customers import manage_customers_menu


def test_customers_menu_quit_immediately(db_session, role_factory, user_factory, monkeypatch):
    # prepare a simple sales user
    role_factory('sales', permissions=['customer:read'])
    user = user_factory(username='cli_sales', role_name='sales')
    # simulate prompt: choose 'Retour' immediately
    inputs = iter(['3'])

    monkeypatch.setattr('click.prompt', lambda *args, **kwargs: int(next(inputs)))
    # call menu - should return without exception
    manage_customers_menu(user, db_session, __import__('app.services.permission_service', fromlist=['PermissionService']).PermissionService(db_session))
