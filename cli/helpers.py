import click
from typing import List, Tuple, Any, Optional


def prompt_menu(
    items: List[Tuple[str, Any]],
    prompt: str = 'Choix',
    allow_return: bool = True,
    return_label: str = '0=Retour',
    empty_message: Optional[str] = None,
) -> Optional[Any]:
    """Affiche un menu numéroté et retourne la value choisie.
    Si rien n'est choisi, retourne None.
    Si allow_return est True, ajoute une option de retour au menu.
    

    """
    if not items:
        if empty_message:
            click.echo(f"\n{empty_message}")
        if allow_return:
            while True:
                click.echo("")
                choice = click.prompt(f"{prompt} ({return_label})", type=int)
                if choice == 0:
                    return None
                click.echo("Choix invalide")
        return None

    while True:
        for idx, (label, _) in enumerate(items, start=1):
            click.echo(f"{idx}. {label}")
        click.echo("")
        suffix = f" ({return_label})" if allow_return else ""
        choice = click.prompt(f"{prompt}{suffix}", type=int)
        if allow_return and choice == 0:
            return None
        if 1 <= choice <= len(items):
            return items[choice - 1][1]
        click.echo("Choix invalide")
