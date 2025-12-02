from app.services.contract_service import ContractService
import click
from cli.helpers import prompt_select_option, prompt_list_or_empty, prompt_detail_actions
from app.db.transaction import transactional


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
    # check permissions even if menu only shows option if allowed
    if not perm_service.can_create_contract(user):
        click.echo('Permission refusée')
        return
    try:
        total_amount = click.prompt('Montant total')
        signed_input = click.prompt('Signé ? (o/n)', default='n')
        signed = signed_input.lower().startswith('o')
        balance_due = click.prompt('Balance due', default=str(total_amount))
        customer_id = click.prompt('ID client associé')
        fields = {
            'total_amount': total_amount,
            'signed': signed,
            'balance_due': balance_due,
            'customer_id': customer_id,
        }
        with transactional(session):
            new_contract = contract_service.create(user, **fields)
        click.echo(f'Contrat créé id={new_contract.id}')
    except Exception as e:
        click.echo(f'Erreur création: {e}')

def update_contract(user, session, perm_service, contract_id):
    from app.models.contract import Contract
    contract_service = ContractService(session, perm_service)
    contract = session.get(Contract, contract_id)
    if not contract:
        click.echo('Contrat introuvable')
        return
    if not perm_service.can_update_contract(user, contract):
        click.echo('Permission refusée')
        return
    mod_fields = [
        ('Montant total', 'total_amount'),
        ('Balance due', 'balance_due'),
        ('Signé (o/n)', 'signed'),
        ('ID client', 'customer_id'),
    ]
    updates = {}
    while True:
        # utilise le helper de sélection
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
        else:
            val = new_val
        updates[field] = val
        try:
            with transactional(session):
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
        click.echo('Permission refusée')
        return
    try:
        confirm = click.prompt('Confirmer suppression ? (o/n)', default='n')
        if confirm.lower().startswith('o'):
            with transactional(session):
                contract_service.delete(user, contract.id)
            click.echo('Contrat supprimé')
    except Exception as e:
        click.echo(f'Erreur: {e}')

def list_all_contracts(user, session, perm_service):
    contract_service = ContractService(session, perm_service)
    try:
        contracts = contract_service.list_all(user)
        contract_options = [(f"{c.id}: lié au client {c.customer.company_name}", c.id) for c in contracts]
        choice = prompt_list_or_empty(contract_options, empty_message='Aucun contrat', prompt_text='Choisir contrat')
        if choice is None:
            return
        display_detail_contracts(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def my_contracts(user, session, perm_service):
    contract_service = ContractService(session, perm_service)
    try:
        # role/ownership logic handled in the view
        if user.role.name == 'management':
            contracts = contract_service.list_by_management_user(user.id)
        elif user.role.name == 'sales':
            customer_ids = [c.id for c in user.customers]
            contracts = contract_service.list_by_customer_ids(customer_ids)
        else:
            contracts = []
        click.echo('\nListe de mes contrats:')
        contract_options = [
            (
                f"{c.id}: {getattr(c, 'contract_id', '')} - "
                f"{(c.customer.company_name if c.customer and getattr(c.customer, 'company_name', None) else (c.customer.customer_first_name + ' ' + c.customer.customer_last_name if c.customer else 'N/A'))}",
                c.id,
            )
            for c in contracts
        ]
        choice = prompt_list_or_empty(contract_options, empty_message="Vous n'avez pas encore de contrat", prompt_text='Choisir contrat')
        if choice is None:
            return
        display_detail_contracts(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def my_unsigned_contracts(user, session, perm_service):
    contract_service = ContractService(session, perm_service)
    try:
        # filter contracts according to role/ownership in view
        if user.role.name == 'management':
            contracts = [c for c in contract_service.list_by_management_user(user.id) if not c.signed]
        elif user.role.name == 'sales':
            customer_ids = [c.id for c in user.customers]
            contracts = [c for c in contract_service.list_by_customer_ids(customer_ids) if not c.signed]
        else:
            contracts = []
        # Affichage similaire à `my_contracts`
        click.echo('\nListe de mes contrats non signés:')
        contract_options = [
            (
                f"{c.id}: {getattr(c, 'contract_id', '')} - "
                f"{(c.customer.company_name if c.customer and getattr(c.customer, 'company_name', None) else (c.customer.customer_first_name + ' ' + c.customer.customer_last_name if c.customer else 'N/A'))}",
                c.id,
            )
            for c in contracts
        ]
        choice = prompt_list_or_empty(contract_options, empty_message="Vous n'avez pas de contrat non signé", prompt_text='Choisir contrat')
        if choice is None:
            return
        display_detail_contracts(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def my_unpaid_contracts(user, session, perm_service):
    contract_service = ContractService(session, perm_service)
    try:
        if user.role.name == 'management':
            contracts = [c for c in contract_service.list_by_management_user(user.id) if c.balance_due > 0]
        elif user.role.name == 'sales':
            customer_ids = [c.id for c in user.customers]
            contracts = [c for c in contract_service.list_by_customer_ids(customer_ids) if c.balance_due > 0]
        else:
            contracts = []
        # Affichage similaire à `my_contracts`
        click.echo('\nListe de mes contrats impayés:')
        contract_options = [
            (
                f"{c.id}: {getattr(c, 'contract_id', '')} - "
                f"{(c.customer.company_name if c.customer and getattr(c.customer, 'company_name', None) else (c.customer.customer_first_name + ' ' + c.customer.customer_last_name if c.customer else 'N/A'))}",
                c.id,
            )
            for c in contracts
        ]
        choice = prompt_list_or_empty(contract_options, empty_message="Vous n'avez pas de contrat impayé", prompt_text='Choisir contrat')
        if choice is None:
            return
        display_detail_contracts(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def display_detail_contracts(user, session, perm_service, contract_id):
    from app.models.contract import Contract
    contract = session.get(Contract, contract_id)
    if not contract:
        click.echo('Contrat introuvable')
        return
    click.echo(f"\nID: {contract.id}\nTotal: {contract.total_amount}\nBalance: {contract.balance_due}\nSigné: {contract.signed}\nClient: {contract.customer_id}\nManager: {contract.user_management_id}")
    actions = []
    if perm_service.user_has_permission(user, 'contract:update'):
        if user.role.name == 'management':
            if contract.user_management_id == user.id:
                actions.append(('Modifier', 'update'))
        else:
            actions.append(('Modifier', 'update'))

    if perm_service.user_has_permission(user, 'contract:delete'):
        if user.role.name == 'management':
            if contract.user_management_id == user.id:
                actions.append(('Supprimer', 'delete'))
        else:
            actions.append(('Supprimer', 'delete'))

    action = prompt_detail_actions(actions, prompt_text='Choix')
    if action is None:
        return
    if action == 'update':
        update_contract(user, session, perm_service, contract_id)
    elif action == 'delete':
        delete_contract(user, session, perm_service, contract_id)
