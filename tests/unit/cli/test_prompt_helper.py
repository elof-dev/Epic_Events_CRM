from cli.helpers import prompt_select_option


class DummyRole:
    def __init__(self, name):
        self.name = name


class DummyUser:
    def __init__(self, role_name):
        self.role = DummyRole(role_name)


def test_prompt_select_option_returns_none_when_zero(monkeypatch):
    options = [('A', 'a'), ('B', 'b')]
    # simulate user entering 0
    def fake_prompt(prompt_text, type=int):
        return 0
    monkeypatch.setattr('click.prompt', fake_prompt)
    res = prompt_select_option(options, prompt='Choix')
    assert res is None


def test_prompt_select_option_returns_action_for_valid_choice(monkeypatch):
    options = [('A', 'a'), ('B', 'b')]
    def fake_prompt(prompt_text, type=int):
        return 2
    monkeypatch.setattr('click.prompt', fake_prompt)
    res = prompt_select_option(options, prompt='Choix')
    assert res == 'b'


def test_prompt_select_option_retries_on_invalid_then_valid(monkeypatch):
    options = [('X', 'x'), ('Y', 'y')]
    calls = {'i': 0}

    def fake_prompt(prompt_text, type=int):
        calls['i'] += 1
        if calls['i'] == 1:
            return 99  # invalid
        return 1

    monkeypatch.setattr('click.prompt', fake_prompt)
    res = prompt_select_option(options, prompt='Choix')
    assert res == 'x'
