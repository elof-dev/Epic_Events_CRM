Epic Events CRM
================

Simple educational CRM written in Python using SQLAlchemy and a CLI.

Setup (Windows cmd.exe):

1. Install poetry: https://python-poetry.org/docs/
2. Copy `.env.example` to `.env` and adjust DB credentials.
3. Install dependencies:

```bash
poetry install
```

Run initialization (drops and recreates database defined in `.env`):

```bash
poetry run python -m app.db.init_db
```

Run CLI:

```bash
poetry run python -m cli.main
```
