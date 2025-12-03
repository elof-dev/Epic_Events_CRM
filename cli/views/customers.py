from app.services.customer_service import CustomerService
import click
from cli.helpers import prompt_select_option, prompt_list_or_empty, prompt_detail_actions
from app.db.transaction import transactional


def get_customer_menu_options(user, perm_service):
    options = []
    if perm_service.can_read_customer(user):
        options.append(('Afficher tous les clients', 'list_all'))
        if getattr(user, 'role', None) is not None and user.role.name == 'sales':
            options.append(('Mes clients', 'mine'))
    if perm_service.can_create_customer(user):
        options.append(('Créer un client', 'create'))
    return options


def main_customer_menu(user, session, perm_service):
    click.echo('\n=== Gestion des clients ===')
    while True:
        options = get_customer_menu_options(user, perm_service)
        action = prompt_select_option(options, prompt='Choix')
        if action is None:
            return
        if action == 'list_all':
            list_all_customers(user, session, perm_service)
        elif action == 'mine':
            my_customers(user, session, perm_service)
        elif action == 'create':
            create_customer(user, session, perm_service)


def create_customer(user, session, perm_service):
    cust_service = CustomerService(session, perm_service)
    # check permissions even if menu only shows option if allowed
    if not perm_service.can_create_customer(user):
        click.echo("Permission refusée")
        return
    try:
        first = click.prompt('Prénom')
        last = click.prompt('Nom')
        email = click.prompt('Email')
        company = click.prompt('Entreprise')
        phone = click.prompt('Téléphone')
        fields = {
            'customer_first_name': first,
            'customer_last_name': last,
            'email': email,
            'company_name': company,
            'phone_number': phone,
        }

        with transactional(session):
            new_customer = cust_service.create(user, **fields)
        click.echo(f'Client créé id={new_customer.id}')
    except Exception as e:
        click.echo(f'Erreur création: {e}')

def update_customer(user, session, perm_service, customer_id):
    from app.models.customer import Customer
    cust_service = CustomerService(session, perm_service)
    customer = session.get(Customer, customer_id)
    if not customer:
        click.echo('Client introuvable')
        return
    if not perm_service.can_update_customer(user, customer):
        click.echo('Permission refusée')
        return
    mod_fields = [
        ('Prénom', 'customer_first_name'),
        ('Nom', 'customer_last_name'),
        ('Email', 'email'),
        ('Entreprise', 'company_name'),
        ('Téléphone', 'phone_number'),
    ]
    updates = {}
    while True:
        field_opts = [(label, field) for label, field in mod_fields]
        field_choice = prompt_select_option(field_opts, prompt='Choisir champ')
        if field_choice is None:
            break
        label = next(lbl for lbl, fld in mod_fields if fld == field_choice)
        field = field_choice
        current_val = getattr(customer, field)
        new_val = click.prompt(label, default=str(current_val) if current_val is not None else '')
        updates[field] = new_val or None
        try:
            with transactional(session):
                cust_service.update(user, customer.id, **updates)
            click.echo('Client mis à jour')
            customer = session.get(Customer, customer_id)
        except Exception as e:
            click.echo(f'Erreur mise à jour: {e}')


def delete_customer(user, session, perm_service, customer_id):
    from app.models.customer import Customer
    cust_service = CustomerService(session, perm_service)
    customer = session.get(Customer, customer_id)
    if not customer:
        click.echo('Client introuvable')
        return
    if not perm_service.can_delete_customer(user, customer):
        click.echo('Permission refusée')
        return
    try:
        confirm = click.prompt('Confirmer suppression ? (o/n)', default='n')
        if confirm.lower().startswith('o'):
            with transactional(session):
                cust_service.delete(user, customer.id)
            click.echo('Client supprimé')
    except Exception as e:
        click.echo(f'Erreur: {e}')


def list_all_customers(user, session, perm_service):
    cust_service = CustomerService(session, perm_service)
    if not perm_service.can_read_customer(user):
        click.echo("Permission refusée")
        return
    try:
        customers = cust_service.list_all(user)
        customer_options = [(f"{c.id}: {c.customer_first_name} {c.customer_last_name}", c.id) for c in customers]
        choice = prompt_list_or_empty(customer_options, empty_message="Aucun client", prompt_text='Choisir client')
        if choice is None:
            return
        display_detail_customers(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def my_customers(user, session, perm_service):
    cust_service = CustomerService(session, perm_service)
    if not perm_service.can_read_customer(user):
        click.echo("Permission refusée")
        return
    try:
        customers = cust_service.list_mine(user)
        click.echo('\nListe de mes clients:')
        customer_options = [(f"{c.id}: {c.customer_first_name} {c.customer_last_name}", c.id) for c in customers]
        choice = prompt_list_or_empty(customer_options, empty_message="Vous n'avez pas encore de client", prompt_text='Choisir client')
        if choice is None:
            return
        display_detail_customers(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def display_detail_customers(user, session, perm_service, customer_id):
    from app.models.customer import Customer
    cust_service = CustomerService(session, perm_service)
    if not perm_service.can_read_customer(user):
        click.echo("Permission refusée")
        return
    customer = session.get(Customer, customer_id)
    if not customer:
        click.echo('Client introuvable')
        return
    click.echo(f"\nID: {customer.id}\nNom: {customer.customer_first_name} {customer.customer_last_name}\nEntreprise: {customer.company_name}\nEmail: {customer.email}\nSales id: {customer.user_sales_id}")
    actions = []
    # Vérification pour affichage des actions possibles
    if perm_service.can_update_customer(user, customer):
        actions.append(('Modifier', 'update'))
    if perm_service.can_delete_customer(user, customer):
        actions.append(('Supprimer', 'delete'))

    action = prompt_detail_actions(actions, prompt_text='Choix')
    if action is None:
        return
    if action == 'update':
        update_customer(user, session, perm_service, customer_id)
    elif action == 'delete':
        delete_customer(user, session, perm_service, customer_id)


