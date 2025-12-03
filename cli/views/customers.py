from app.services.customer_service import CustomerService
import click
from cli.helpers import prompt_select_option, prompt_list_or_empty, prompt_detail_actions
from app.db.transaction import transactional
from sentry_sdk import capture_exception


class CustomersView:
    def __init__(self, session, perm_service):
        self.session = session
        self.perm_service = perm_service

    def get_customer_menu_options(self, user):
        options = []
        if self.perm_service.user_has_permission(user, 'customer:read'):
            options.append(('Afficher tous les clients', 'list_all'))
            if getattr(user, 'role', None) is not None and user.role.name == 'sales':
                options.append(('Mes clients', 'mine'))
        if self.perm_service.user_has_permission(user, 'customer:create'):
            options.append(('Créer un client', 'create'))
        return options

    def main_customer_menu(self, user):
        click.echo('\n=== Gestion des clients ===')
        while True:
            options = self.get_customer_menu_options(user)
            action = prompt_select_option(options, prompt='Choix')
            if action is None:
                return
            if action == 'list_all':
                self.list_all_customers(user)
            elif action == 'mine':
                self.my_customers(user)
            elif action == 'create':
                self.create_customer(user)

    def create_customer(self, user):
        cust_service = CustomerService(self.session, self.perm_service)
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
            with transactional(self.session):
                new_customer = cust_service.create(user, **fields)
            click.echo(f'Client créé id={new_customer.id}')
        except Exception as e:
            capture_exception(e)
            click.echo(f'Erreur création: {e}')

    def update_customer(self, user, customer_id):
        from app.models.customer import Customer
        cust_service = CustomerService(self.session, self.perm_service)
        customer = self.session.get(Customer, customer_id)
        if not customer:
            click.echo('Client introuvable')
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
                with transactional(self.session):
                    cust_service.update(user, customer.id, **updates)
                click.echo('Client mis à jour')
                customer = self.session.get(Customer, customer_id)
            except Exception as e:
                click.echo(f'Erreur mise à jour: {e}')

    def delete_customer(self, user, customer_id):
        from app.models.customer import Customer
        cust_service = CustomerService(self.session, self.perm_service)
        customer = self.session.get(Customer, customer_id)
        if not customer:
            click.echo('Client introuvable')
            return
        try:
            confirm = click.prompt('Confirmer suppression ? (o/n)', default='n')
            if confirm.lower().startswith('o'):
                with transactional(self.session):
                    cust_service.delete(user, customer.id)
                click.echo('Client supprimé')
        except Exception as e:
            click.echo(f'Erreur: {e}')

    def list_all_customers(self, user):
        cust_service = CustomerService(self.session, self.perm_service)
        try:
            customers = cust_service.list_all(user)
            customer_options = [(f"{c.id}: {c.customer_first_name} {c.customer_last_name}", c.id) for c in customers]
            choice = prompt_list_or_empty(customer_options, empty_message="Aucun client", prompt_text='Choisir client')
            if choice is None:
                return
            self.display_detail_customers(user, choice)
        except Exception as e:
            click.echo(f'Erreur: {e}')

    def my_customers(self, user):
        cust_service = CustomerService(self.session, self.perm_service)
        try:
            customers = cust_service.list_mine(user)
            click.echo('\nListe de mes clients:')
            customer_options = [(f"{c.id}: {c.customer_first_name} {c.customer_last_name}", c.id) for c in customers]
            choice = prompt_list_or_empty(customer_options, empty_message="Vous n'avez pas encore de client", prompt_text='Choisir client')
            if choice is None:
                return
            self.display_detail_customers(user, choice)
        except Exception as e:
            click.echo(f'Erreur: {e}')

    def display_detail_customers(self, user, customer_id):
        from app.models.customer import Customer
        cust_service = CustomerService(self.session, self.perm_service)
        customer = self.session.get(Customer, customer_id)
        if not customer:
            click.echo('Client introuvable')
            return
        click.echo(f"\nID: {customer.id}\nNom: {customer.customer_first_name} {customer.customer_last_name}\nEntreprise: {customer.company_name}\nEmail: {customer.email}\nSales id: {customer.user_sales_id}")
        actions = []
        is_customer_owner = getattr(customer, 'user_sales_id', None) == getattr(user, 'id', None)
        if self.perm_service.user_has_permission(user, 'customer:update') and is_customer_owner:
            actions.append(('Modifier', 'update'))
        if self.perm_service.user_has_permission(user, 'customer:delete') and is_customer_owner:
            actions.append(('Supprimer', 'delete'))
        action = prompt_detail_actions(actions, prompt_text='Choix')
        if action is None:
            return
        if action == 'update':
            self.update_customer(user, customer_id)
        elif action == 'delete':
            self.delete_customer(user, customer_id)


