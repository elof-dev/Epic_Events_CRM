import click
from cli.crm_interface import run_interface
from app.db import init_db as init_db_module
import cli.sentry as sentry_module

@click.group()
def cli():
    pass


@cli.command()
def run():
    """Lancer l'interface CLI"""
    # réinitialiser la base de données à chaque démarrage (DROP + CREATE + SEED)
    click.echo('Réinitialisation de la base de données (DROP + CREATE + SEED)...')
    init_db_module.main()
    click.echo('Réinitialisation terminée. Démarrage de l\'interface...')
    # delegate to crm_interface
    sentry_module.init_sentry()
    run_interface()



if __name__ == "__main__":
    cli()
