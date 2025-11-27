import click
from typing import List, Tuple, Any, Optional


def prompt_select_option(options: List[Tuple[str, Any]], prompt: str = 'Choix') -> Optional[Any]:
    """Affiche une liste d'options (label, value) numérotées 1..N et invite l'utilisateur.

    Le prompt affichera "{prompt} (0=Retour)". Si l'utilisateur choisit 0, retourne None.
    Si le choix est valide, retourne la `value` associée. Boucle tant que l'entrée est invalide.
    """
    if not options:
        return None
    while True:
        for i, (label, _) in enumerate(options, start=1):
            click.echo(f"{i}. {label}")
        choice = click.prompt(f"{prompt} (0=Retour)", type=int)
        if choice == 0:
            return None
        if 1 <= choice <= len(options):
            return options[choice - 1][1]
        click.echo("Choix invalide")
