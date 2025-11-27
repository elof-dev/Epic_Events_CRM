from app.services.event_service import EventService
import click
from datetime import datetime


def manage_events_menu(user, session, perm_service):
    click.echo('\n=== Gestion des évènements ===')
    event_service = EventService(session, perm_service)
    while True:
        click.echo('1. Afficher tous les évènements')
        if user.role.name == 'support':
            click.echo('2. Mes évènements')
            opt_offset = 1
        else:
            opt_offset = 0
        click.echo(f"{3+opt_offset}. Créer un évènement")
        click.echo(f"{4+opt_offset}. Evènements sans support assigned (management only)")
        click.echo(f"{5+opt_offset}. Retour")
        choice = click.prompt('Choix', type=int)
        if choice == 1:
            events = event_service.list_all(user)
            print_events(events)
        elif choice == 2 and opt_offset == 1:
            events = event_service.list_mine(user)
            print_events(events)
        elif choice == 3 + opt_offset:
            # create event
            try:
                contract_id = int(click.prompt('ID du contrat lié'))
                event_name = click.prompt('Nom de l\'évènement')
                event_number = click.prompt('Numéro d\'évènement')
                start_raw = click.prompt('Date/heure de début (YYYY-MM-DD HH:MM)')
                end_raw = click.prompt('Date/heure de fin (YYYY-MM-DD HH:MM)')
                start_dt = datetime.fromisoformat(start_raw.replace(' ', 'T'))
                end_dt = datetime.fromisoformat(end_raw.replace(' ', 'T'))
                location = click.prompt('Lieu', default='')
                attendees = click.prompt('Nombre participants', default='0')
                support_id_raw = click.prompt('ID support (optionnel)', default='')
                fields = {
                    'contract_id': contract_id,
                    'event_name': event_name,
                    'event_number': event_number,
                    'start_datetime': start_dt,
                    'end_datetime': end_dt,
                    'location': location or None,
                    'attendees': int(attendees) if attendees else None,
                    'user_support_id': int(support_id_raw) if support_id_raw else None,
                }
                new_e = event_service.create(user, **fields)
                click.echo(f'Evènement créé id={new_e.id}')
            except Exception as e:
                click.echo(f'Erreur création: {e}')
        elif choice == 4 + opt_offset:
            # events without support
            all_events = event_service.list_all(user)
            no_support = [e for e in all_events if e.user_support_id is None]
            print_events(no_support)
        else:
            break


def print_events(events):
    click.echo('\nEvènements:')
    for e in events:
        click.echo(f"{e.id}: {e.event_name} - {e.event_number} client={e.customer_id} support={e.user_support_id}")
