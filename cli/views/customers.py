from app.services.customer_service import CustomerService
from app.models.customer import Customer
import click


def manage_customers_menu(user, session, perm_service):
    click.echo('\n=== Gestion des clients ===')
    cust_service = CustomerService(session, perm_service)
    while True:
        # menu options
        click.echo('1. Afficher tous les clients')
        idx = 2
        if user.role.name == 'sales':
            click.echo(f'{idx}. Mes clients')
            idx += 1
        click.echo(f'{idx}. Créer un client')
        idx += 1
        click.echo(f'{idx}. Retour')

        choice = click.prompt('Choix', type=int)
        if choice == 1:
            customers = cust_service.list_all(user)
            print_customers(customers)
            handle_customer_detail_loop(user, session, perm_service, cust_service)
        elif user.role.name == 'sales' and choice == 2:
            customers = cust_service.list_mine(user)
            print_customers(customers)
            handle_customer_detail_loop(user, session, perm_service, cust_service)
        elif choice == (3 if user.role.name == 'sales' else 2):
            # create
            try:
                first = click.prompt('Prénom')
                last = click.prompt('Nom')
                email = click.prompt('Email')
                company = click.prompt('Entreprise')
                phone = click.prompt('Téléphone', default='')
                fields = {
                    'customer_first_name': first,
                    'customer_last_name': last,
                    'email': email,
                    'company_name': company,
                    'phone': phone or None,
                }
                new_c = cust_service.create(user, **fields)
                click.echo(f'Client créé id={new_c.id}')
            except Exception as e:
                click.echo(f'Erreur création: {e}')
        else:
            break


def handle_customer_detail_loop(user, session, perm_service, cust_service):
    while True:
        sel = click.prompt('Choisissez un id de client (0 pour retour)', type=int)
        if sel == 0:
            break
        c = cust_service.repo.get_by_id(sel)
        if not c:
            click.echo('Client introuvable')
            continue
        click.echo(f"ID: {c.id}\nNom: {c.customer_first_name} {c.customer_last_name}\nEntreprise: {c.company_name}\nEmail: {c.email}\nSales id: {c.user_sales_id}")
        click.echo('1. Modifier\n2. Supprimer\n3. Retour')
        a = click.prompt('Choix', type=int)
        if a == 1:
            fields = {}
            new_first = click.prompt('Prénom', default=c.customer_first_name)
            new_last = click.prompt('Nom', default=c.customer_last_name)
            new_email = click.prompt('Email', default=c.email)
            new_company = click.prompt('Entreprise', default=c.company_name)
            fields.update({'customer_first_name': new_first, 'customer_last_name': new_last, 'email': new_email, 'company_name': new_company})
            try:
                cust_service.update(user, c.id, **fields)
                click.echo('Client mis à jour')
            except Exception as e:
                click.echo(f'Erreur: {e}')
        elif a == 2:
            try:
                cust_service.delete(user, c.id)
                click.echo('Client supprimé')
                break
            except Exception as e:
                click.echo(f'Erreur: {e}')
        else:
            continue


def print_customers(customers):
    click.echo('\nClients:')
    for c in customers:
        click.echo(f"{c.id}: {c.customer_first_name} {c.customer_last_name} - {c.company_name} (sales_id={c.user_sales_id})")
