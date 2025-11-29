import click
from cli.crm_interface import run_interface
from app.db import init_db as init_db_module


# `cli.crm_interface.run_interface` gère la session et l'authentification.


# The main top-level orchestration has been moved to `cli.crm_interface.run_interface`.
# This keeps `main` as the CLI entrypoint.




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
    run_interface()


if __name__ == "__main__":
    cli()
