from app.services.event_service import EventService
import click
from datetime import datetime
from cli.helpers import prompt_select_option, prompt_list_or_empty, prompt_detail_actions
from app.db.transaction import transactional

def get_event_menu_options(user, perm_service):
    """Return the list of (label, action) menu options for the given user.

    This is extracted to a helper to make unit testing the CLI menu easier.
    """
    options = []
    if perm_service.user_has_permission(user, 'event:read'):
        options.append(('Afficher tous les évènements', 'all'))
        if user.role.name == 'support':
            options.append(('Mes évènements', 'mine'))
    if user.role.name == 'sales' and perm_service.user_has_permission(user, 'event:create'):
        options.append(('Créer un évènement', 'create'))
    if user.role.name == 'management' and perm_service.user_has_permission(user, 'event:read'):
        options.append(('Evènements sans support assigned', 'nosupport'))
    return options


def main_event_menu(user, session, perm_service):
    click.echo('\n=== Gestion des évènements ===')
    while True:
        options = get_event_menu_options(user, perm_service)
        action = prompt_select_option(options, prompt='Choix')
        if action is None:
            return
        if action == 'all':
            list_all_events(user, session, perm_service)
        elif action == 'mine':
            my_events(user, session, perm_service)
        elif action == 'create':
            create_event(user, session, perm_service)
        elif action == 'nosupport':
            events_without_support(user, session, perm_service)


def create_event(user, session, perm_service):
    event_service = EventService(session, perm_service)
    # check des permissions même si le menu n'affiche cette action que si autorisée
    if not perm_service.user_has_permission(user, 'event:create'):
        click.echo('Permission refusée')
        return
    try:
        contract_id = click.prompt('ID du contrat lié')
        customer_id = click.prompt('ID du client lié')
        event_name = click.prompt('Nom de l\'évènement')
        start_datetime = click.prompt('Date/heure de début (YYYY-MM-DD HH:MM)', default='')
        end_datetime = click.prompt('Date/heure de fin (YYYY-MM-DD HH:MM)', default='')
        location = click.prompt('Lieu', default='')
        attendees = click.prompt('Nombre participants', default='0')
        support_id = click.prompt('ID support', default='')
        fields = {
            'contract_id': contract_id,
            'customer_id': customer_id,
            'event_name': event_name,
            'start_datetime': start_datetime or None,
            'end_datetime': end_datetime or None,
            'location': location or None,
            'attendees': attendees or None,
            'user_support_id': support_id or None,
        }
        # enforce business rule at view level: contract must be signed and belong to this sales user
        from app.models.contract import Contract
        contract = session.get(Contract, contract_id)
        if not contract:
            click.echo('Contrat introuvable ou non accessible')
            return
        if not contract.signed or contract.customer.user_sales_id != user.id:
            click.echo("Impossible de créer l'évènement: le contrat doit être signé et appartenir au commercial")
            return
        with transactional(session):
            new_e = event_service.create(user, **fields)
        click.echo(f'Evènement créé id={new_e.id}')
    except Exception as e:
        click.echo(f'Erreur création: {e}')


def list_all_events(user, session, perm_service):
    event_service = EventService(session, perm_service)
    try:
        events = event_service.list_all(user)
        opts = [(f"{e.id}: {e.event_name}", e.id) for e in events]
        choice = prompt_list_or_empty(opts, empty_message='Aucun évènement', prompt_text='Choisir évènement')
        if choice is None:
            return
        display_detail_events(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def my_events(user, session, perm_service):
    event_service = EventService(session, perm_service)
    try:
        # role/ownership logic handled in the view
        if user.role.name == 'support':
            events = event_service.list_by_support_user(user.id)
        elif user.role.name == 'sales':
            customer_ids = [c.id for c in user.customers]
            events = []
            for cid in customer_ids:
                events.extend(event_service.list_by_customer(cid))
        else:
            events = []
        if not events:
            click.echo('\nAucun évènement')
            try:
                while True:
                    c = click.prompt('Choix (0=Retour)', type=int)
                    if c == 0:
                        break
            except Exception:
                pass
            return
        opts = [(f"{e.id}: {e.event_name}", e.id) for e in events]
        choice = prompt_list_or_empty(opts, empty_message='Aucun évènement', prompt_text='Choisir évènement')
        if choice is None:
            return
        display_detail_events(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def events_without_support(user, session, perm_service):
    event_service = EventService(session, perm_service)
    try:
        events = [e for e in event_service.list_all(user) if e.user_support_id is None]
        if not events:
            click.echo('\nAucun évènement')
            try:
                while True:
                    c = click.prompt('Choix (0=Retour)', type=int)
                    if c == 0:
                        break
            except Exception:
                pass
            return
        opts = [(f"{e.id}: {e.event_name}", e.id) for e in events]
        choice = prompt_list_or_empty(opts, empty_message='Aucun évènement', prompt_text='Choisir évènement')
        if choice is None:
            return
        display_detail_events(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def display_list_events(events):
    click.echo('\nEvènements:')
    for e in events:
        print_event(e)


def display_detail_events(current_user, session, perm_service, event_id):
    from app.models.event import Event
    event_service = EventService(session, perm_service)
    event = session.get(Event, event_id)
    if not event:
        click.echo('Evènement introuvable')
        return
    click.echo(f"\nID: {event.id}\nNom: {event.event_name}\nNuméro: {event.event_id}\nContract: {event.contract_id}\nClient: {event.customer_id}\nDébut: {event.start_datetime}\nFin: {event.end_datetime}\nLieu: {event.location}\nParticipants: {event.attendees}\nSupport: {event.user_support_id}")
    can_update = perm_service.user_has_permission(current_user, 'event:update')
    can_delete = perm_service.user_has_permission(current_user, 'event:delete')
    actions = []
    if can_update:
        actions.append(('Modifier', 'update'))
    if can_delete:
        actions.append(('Supprimer', 'delete'))
    action = prompt_detail_actions(actions, prompt_text='Choix')
    if action is None:
        return
    if action == 'update':
        update_event(current_user, session, perm_service, event_id)
    elif action == 'delete':
        delete_event(current_user, session, perm_service, event_id)


def update_event(current_user, session, perm_service, event_id):
    from app.models.event import Event
    event_service = EventService(session, perm_service)
    event = session.get(Event, event_id)
    if not event:
        click.echo('Evènement introuvable')
        return
    if not perm_service.user_has_permission(current_user, 'event:update'):
        click.echo('Permission refusée: mise à jour impossible')
        return
    # management can only update support assignment (enforced at view level)
    if current_user.role.name == 'management':
        new_support = click.prompt('ID nouveau support (laisser vide pour annuler)', default='')
        if not new_support:
            click.echo('Annulé')
            return
        try:
            with transactional(session):
                event_service.update(current_user, event.id, user_support_id=int(new_support))
            click.echo('Support mis à jour')
        except Exception as e:
            click.echo(f'Erreur mise à jour: {e}')
        return

    mod_fields = [
        ('Client', 'customer_id'),
        ('Contrat', 'contract_id'),
        ('Nom', 'event_name'),
        ('Début (YYYY-MM-DD HH:MM)', 'start_datetime'),
        ('Fin (YYYY-MM-DD HH:MM)', 'end_datetime'),
        ('Lieu', 'location'),
        ('Participants', 'attendees'),
        ('ID support', 'user_support_id'),
    ]
    while True:
        field_opts = [(label, field) for label, field in mod_fields]
        field_choice = prompt_select_option(field_opts, prompt='Choisir champ')
        if field_choice is None:
            break
        label = next(lbl for lbl, fld in mod_fields if fld == field_choice)
        field = field_choice
        current_val = getattr(event, field)
        new_raw = click.prompt(label, default=str(current_val) if current_val is not None else '')
        if field in ('start_datetime', 'end_datetime') and new_raw:
            val = new_raw
        elif field == 'attendees':
            val = new_raw or None
        elif field == 'user_support_id':
            val = new_raw or None
        else:
            val = new_raw
        try:
            with transactional(session):
                event_service.update(current_user, event.id, **{field: val})
            click.echo('Champ mis à jour')
            event = session.get(Event, event_id)
        except Exception as e:
            click.echo(f'Erreur mise à jour: {e}')


def delete_event(current_user, session, perm_service, event_id):
    from app.models.event import Event
    event_service = EventService(session, perm_service)
    event = session.get(Event, event_id)
    if not event:
        click.echo('Evènement introuvable')
        return
    if not perm_service.user_has_permission(current_user, 'event:delete'):
        click.echo('Permission refusée: suppression impossible')
        return
    try:
        confirm = click.prompt('Confirmer suppression ? (o/n)', default='n')
        if confirm.lower().startswith('o'):
            with transactional(session):
                event_service.delete(current_user, event.id)
            click.echo('Evènement supprimé')
    except Exception as e:
        click.echo(f'Erreur suppression: {e}')


def print_event(e):
    click.echo(f"{e.id}: {e.event_name} - {e.event_id} client={e.customer_id} support={e.user_support_id}")
