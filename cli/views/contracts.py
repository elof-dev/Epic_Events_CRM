from app.services.contract_service import ContractService
import click


def manage_contracts_menu(user, session, perm_service):
    click.echo('\n=== Gestion des contrats ===')
    contract_service = ContractService(session, perm_service)
    while True:
        click.echo('1. Afficher tous les contrats')
        click.echo('2. Mes contrats')
        click.echo('3. Mes contrats non signés')
        click.echo('4. Mes contrats non payés')
        click.echo('5. Créer un contrat')
        click.echo('6. Retour')
        choice = click.prompt('Choix', type=int)
        if choice == 1:
            contracts = contract_service.list_all(user)
            print_contracts(contracts)
        elif choice == 2:
            contracts = contract_service.list_mine(user)
            print_contracts(contracts)
        elif choice == 3:
            contracts = [c for c in contract_service.list_mine(user) if not c.signed]
            print_contracts(contracts)
        elif choice == 4:
            contracts = [c for c in contract_service.list_mine(user) if c.balance_due > 0]
            print_contracts(contracts)
        elif choice == 5:
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
        else:
            break


def print_contracts(contracts):
    click.echo('\nContrats:')
    for c in contracts:
        click.echo(f"{c.id}: {c.contract_number} - total={c.total_amount} balance={c.balance_due} signed={c.signed} customer_id={c.customer_id} manager_id={c.user_management_id}")
