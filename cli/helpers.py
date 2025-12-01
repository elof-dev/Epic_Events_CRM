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


def prompt_list_or_empty(options: List[Tuple[str, Any]], empty_message: str = 'Aucun élément', prompt_text: str = 'Choix') -> Optional[Any]:
    """If `options` is empty, print `empty_message` and wait for the user to press 0 on the standard prompt.
    Otherwise, delegate to `prompt_select_option` to show the numbered menu.

    Returns the selected value or `None` when the user chooses to return.
    """
    if not options:
        click.echo(f"\n{empty_message}")
        try:
            while True:
                c = click.prompt(f"{prompt_text} (0=Retour)", type=int)
                if c == 0:
                    return None
        except Exception:
            return None
    return prompt_select_option(options, prompt=prompt_text)


def prompt_detail_actions(actions: List[Tuple[str, Any]], prompt_text: str = 'Choix') -> Optional[Any]:
    """If `actions` is empty, show the standard prompt and wait for 0, otherwise use `prompt_select_option`.

    Returns the selected action value or None.
    """
    if not actions:
        try:
            c = click.prompt(f"{prompt_text} (0=Retour)", type=int)
            if c == 0:
                return None
        except Exception:
            return None
        return None
    return prompt_select_option(actions, prompt=prompt_text)
