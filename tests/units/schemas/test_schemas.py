from datetime import datetime, timedelta
import pytest
from app.schemas import user as user_schema
from app.schemas import customer as customer_schema
from app.schemas import event as event_schema
from app.schemas import contract as contract_schema
from pydantic import ValidationError


def test_user_create_normalise_et_valide():
    """Les champs sont nettoyés et validés automatiquement."""
    payload = {
        "user_first_name": " Alice ",
        "user_last_name": " Wonder ",
        "username": "cooluser",
        "email": " TEST@EXAMPLE.COM ",
        "phone_number": "  +33123456789 ",
        "role_id": 2,
        "password": "securepass",
    }
    validated = user_schema.UserCreate(**payload)
    assert validated.user_first_name == "Alice"
    assert validated.email == "test@example.com"
    assert validated.phone_number == "+33123456789"


def test_user_create_rejette_pseudo_invalid():
    """Le nom d’utilisateur ne doit contenir que lettres/chiffres."""
    with pytest.raises(ValidationError):
        user_schema.UserCreate(
            user_first_name="Bob",
            user_last_name="Builder",
            username="bad user!",
            email="bob@example.com",
            phone_number="+33123456789",
            role_id=1,
            password="securepass",
        )


def test_customer_create_rejette_nom_et_telephone_invalides():
    """Les validateurs de nom et téléphone sécurisent les entrées."""
    with pytest.raises(ValidationError):
        customer_schema.CustomerCreate(
            user_sales_id=1,
            customer_first_name="1234",
            customer_last_name="Client",
            email="c@example.com",
            phone_number="+33123456789",
            company_name="Acme",
        )
    with pytest.raises(ValidationError):
        customer_schema.CustomerCreate(
            user_sales_id=1,
            customer_first_name="Alice",
            customer_last_name="Wonder",
            email="c@example.com",
            phone_number="ABC123",
            company_name="Acme",
        )


def test_event_create_dates_futures_et_attendees():
    """Les dates doivent être dans le futur, et les participants non négatifs."""
    now = datetime.now()
    payload = {
        "contract_id": 1,
        "customer_id": 2,
        "event_name": "Lancement",
        "start_datetime": now + timedelta(days=1),
        "end_datetime": now + timedelta(days=2),
        "attendees": 10,
    }
    evt = event_schema.EventCreate(**payload)
    assert evt.event_name == "Lancement"
    assert evt.attendees == 10
    with pytest.raises(ValidationError):
        event_schema.EventCreate(
            **{**payload, "end_datetime": now - timedelta(days=1)}
        )
    with pytest.raises(ValidationError):
        event_schema.EventCreate(**{**payload, "attendees": -5})


def test_contract_balance_ne_peut_pas_depasser_total():
    """Le `balance_due` ne peut être supérieur au `total_amount`."""
    contract_schema.ContractCreate(
        total_amount=100,
        balance_due=50,
        customer_id=1,
        user_management_id=1,
    )
    with pytest.raises(ValidationError):
        contract_schema.ContractCreate(
            total_amount=100,
            balance_due=150,
            customer_id=1,
            user_management_id=1,
        )