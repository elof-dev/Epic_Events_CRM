from app.services.contract_service import ContractService
import click
from cli.helpers import prompt_select_option


def get_contracts_menu_options(user, perm_service):
    """Return available (label, action) options for contracts menu (excludes return)."""
    options = []
    if perm_service.user_has_permission(user, 'contract:read'):
        if perm_service.can_create_contract(user):
            options.append(('Créer un contrat', 'create'))
        options.append(('Afficher tous les contrats', 'list_all'))
        options.append(('Mes contrats', 'mine'))
        options.append(('Mes contrats non signés', 'unsigned'))
        options.append(('Mes contrats non payés', 'unpaid'))

    return options


def main_contract_menu(user, session, perm_service):
    click.echo('\n=== Gestion des contrats ===')
    contract_service = ContractService(session, perm_service)
    while True:
        options = get_contracts_menu_options(user, perm_service)
        action = prompt_select_option(options, prompt='Choix')
        if action is None:
            return
        if action == 'list_all':
            list_all_contracts(user, session, perm_service)
        elif action == 'mine':
            my_contracts(user, session, perm_service)
        elif action == 'unsigned':
            my_unsigned_contracts(user, session, perm_service)
        elif action == 'unpaid':
            my_unpaid_contracts(user, session, perm_service)
        elif action == 'create':
            create_contract(user, session, perm_service)


def create_contract(user, session, perm_service):
    contract_service = ContractService(session, perm_service)
    if not perm_service.can_create_contract(user):
        click.echo('Permission refusée: création de contrat impossible')
        return
    try:
        contract_number = click.prompt('Numéro de contrat')
        total_amount = float(click.prompt('Montant total', default='0'))
        signed_input = click.prompt('Signé ? (o/n)', default='n')
        signed = signed_input.lower().startswith('o')
        balance_due = float(click.prompt('Balance due', default=str(total_amount)))
        customer_id = int(click.prompt('ID client associé'))
        manager_id = int(click.prompt('ID manager (management user)'))
        fields = {
            'contract_number': contract_number,
            'total_amount': total_amount,
            'signed': signed,
            'balance_due': balance_due,
            'customer_id': customer_id,
            'user_management_id': manager_id,
        }
        new_c = contract_service.create(user, **fields)
        click.echo(f'Contrat créé id={new_c.id}')
    except Exception as e:
        click.echo(f'Erreur création: {e}')


def list_all_contracts(user, session, perm_service):
    contract_service = ContractService(session, perm_service)
    try:
        contracts = contract_service.list_all(user)
        display_list_contracts(contracts)
        sel = click.prompt('\nChoisissez un id de contrat (0=Retour)', type=int)
        if sel == 0:
            return
        display_detail_contracts(user, session, perm_service, sel)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def my_contracts(user, session, perm_service):
    contract_service = ContractService(session, perm_service)
    try:
        contracts = contract_service.list_mine(user)
        display_list_contracts(contracts)
        sel = click.prompt('\nChoisissez un id de contrat (0=Retour)', type=int)
        if sel == 0:
            return
        display_detail_contracts(user, session, perm_service, sel)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def my_unsigned_contracts(user, session, perm_service):
    contract_service = ContractService(session, perm_service)
    try:
        contracts = [c for c in contract_service.list_mine(user) if not c.signed]
        display_list_contracts(contracts)
        sel = click.prompt('\nChoisissez un id de contrat (0=Retour)', type=int)
        if sel == 0:
            return
        display_detail_contracts(user, session, perm_service, sel)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def my_unpaid_contracts(user, session, perm_service):
    contract_service = ContractService(session, perm_service)
    try:
        contracts = [c for c in contract_service.list_mine(user) if c.balance_due > 0]
        display_list_contracts(contracts)
        sel = click.prompt('\nChoisissez un id de contrat (0=Retour)', type=int)
        if sel == 0:
            return
        display_detail_contracts(user, session, perm_service, sel)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def display_list_contracts(contracts):
    click.echo('\nContrats:')
    for c in contracts:
        print_contract(c)


def display_detail_contracts(user, session, perm_service, contract_id):
    from app.models.contract import Contract
    contract = session.get(Contract, contract_id)
    if not contract:
        click.echo('Contrat introuvable')
        return
    click.echo(f"\nID: {contract.id}\nNuméro: {contract.contract_number}\nTotal: {contract.total_amount}\nBalance: {contract.balance_due}\nSigné: {contract.signed}\nClient: {contract.customer_id}\nManager: {contract.user_management_id}")
    # available actions
    can_update = perm_service.user_has_permission(user, 'contract:update') and perm_service.can_update_contract(user, contract)
    can_delete = perm_service.user_has_permission(user, 'contract:delete') and perm_service.can_delete_contract(user)
    actions = []
    if can_update:
        actions.append(('Modifier', 'update'))
    if can_delete:
        actions.append(('Supprimer', 'delete'))

    action = prompt_select_option(actions, prompt='Choix')
    if action is None:
        return
    if action == 'update':
        update_contract(user, session, perm_service, contract_id)
    elif action == 'delete':
        delete_contract(user, session, perm_service, contract_id)


def update_contract(user, session, perm_service, contract_id):
    from app.models.contract import Contract
    contract_service = ContractService(session, perm_service)
    contract = session.get(Contract, contract_id)
    if not contract:
        click.echo('Contrat introuvable')
        return
    if not perm_service.can_update_contract(user, contract):
        click.echo('Permission refusée: mise à jour impossible')
        return
    mod_fields = [
        ('Numéro', 'contract_number'),
        ('Montant total', 'total_amount'),
        ('Balance due', 'balance_due'),
        ('Signé (o/n)', 'signed'),
        ('ID client', 'customer_id'),
        ('ID manager', 'user_management_id'),
    ]
    updates = {}
    while True:
        # Use central prompt helper so 0=Retour is consistent across the app
        field_opts = [(label, field) for label, field in mod_fields]
        field_choice = prompt_select_option(field_opts, prompt='Choisir champ')
        if field_choice is None:
            break
        label = next(lbl for lbl, fld in mod_fields if fld == field_choice)
        field = field_choice
        current_val = getattr(contract, field)
        new_val = click.prompt(label, default=str(current_val) if current_val is not None else '')
        if field == 'signed':
            val = new_val.lower().startswith('o')
        elif field in ('total_amount', 'balance_due'):
            val = float(new_val)
        elif field in ('customer_id', 'user_management_id'):
            val = int(new_val)
        else:
            val = new_val
        updates[field] = val
        try:
            contract_service.update(user, contract.id, **updates)
            click.echo('Contrat mis à jour')
            contract = session.get(Contract, contract_id)
        except Exception as e:
            click.echo(f'Erreur mise à jour: {e}')


def delete_contract(user, session, perm_service, contract_id):
    from app.models.contract import Contract
    contract_service = ContractService(session, perm_service)
    contract = session.get(Contract, contract_id)
    if not contract:
        click.echo('Contrat introuvable')
        return
    if not perm_service.can_delete_contract(user):
        click.echo('Permission refusée: suppression impossible')
        return
    try:
        confirm = click.prompt('Confirmer suppression ? (o/n)', default='n')
        if confirm.lower().startswith('o'):
            contract_service.delete(user, contract.id)
            click.echo('Contrat supprimé')
    except Exception as e:
        click.echo(f'Erreur: {e}')


def print_contract(c):
    click.echo(f"{c.id}: {c.contract_number} - total={c.total_amount} balance={c.balance_due} signed={c.signed} customer_id={c.customer_id} manager_id={c.user_management_id}")

