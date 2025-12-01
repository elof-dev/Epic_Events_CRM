import builtins
import click
import pytest
from cli.helpers import prompt_select_option


def test_prompt_select_option_returns_selected_value(monkeypatch, capsys):
    options = [("One", 1), ("Two", 2), ("Three", 3)]
    # monkeypatch click.prompt to simulate user choosing option 2
    monkeypatch.setattr(click, "prompt", lambda *args, **kwargs: 2)
    out = prompt_select_option(options, prompt="Test")
    assert out == 2


def test_prompt_select_option_handles_return_zero(monkeypatch):
    options = [("A", "a")]
    monkeypatch.setattr(click, "prompt", lambda *args, **kwargs: 0)
    assert prompt_select_option(options, prompt="P") is None


def test_prompt_select_option_no_options_returns_none():
    assert prompt_select_option([], prompt="P") is None
