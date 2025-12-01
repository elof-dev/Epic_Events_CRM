import pytest
from pydantic import ValidationError
from app.schemas.user import BaseUser, UserCreate, UserUpdate


def test_baseuser_name_validators_accept_valid_names():
    data = {
        "user_first_name": "Élodie",
        "user_last_name": "Dupont"
    }
    b = BaseUser(**data)
    assert b.user_first_name == "Élodie"
    assert b.user_last_name == "Dupont"


@pytest.mark.parametrize("bad_name", ["", "123", "Jean@", "A" * 101])
def test_baseuser_name_invalid_raises(bad_name):
    with pytest.raises(ValidationError):
        BaseUser(user_first_name=bad_name)


def test_username_validator_accepts_alnum():
    b = BaseUser(username="User123")
    assert b.username == "User123"


@pytest.mark.parametrize("bad_user", ["user name", "user!", ""]) 
def test_username_invalid_raises(bad_user):
    with pytest.raises(ValidationError):
        BaseUser(username=bad_user)


def test_phone_validator_accepts_numbers_and_plus():
    b = BaseUser(phone_number="+33123456789")
    assert b.phone_number == "+33123456789"


@pytest.mark.parametrize("bad_phone", ["abc", "12-34", "", "+"])
def test_phone_invalid_raises(bad_phone):
    with pytest.raises(ValidationError):
        BaseUser(phone_number=bad_phone)


def test_password_length_constraints():
    with pytest.raises(ValidationError):
        BaseUser(password="short")
    long_pw = "p" * 101
    with pytest.raises(ValidationError):
        BaseUser(password=long_pw)
    # acceptable
    b = BaseUser(password="goodpassword123")
    assert b.password == "goodpassword123"


def test_usercreate_requires_fields():
    # missing required fields should raise
    with pytest.raises(ValidationError):
        UserCreate()


def test_userupdate_allows_optional_fields():
    u = UserUpdate()
    assert u.user_first_name is None
    # partial update should validate individual fields
    u2 = UserUpdate(username="validuser")
    assert u2.username == "validuser"
