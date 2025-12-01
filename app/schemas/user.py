from typing import Optional, Annotated
import re
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

"""
Schémas Pydantic pour l'entité User.
Permettent la validation des données d'entrée/sortie 
pour les opérations CRUD sur les utilisateurs.
"""

# Patterns de validation
NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$")
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9]+$")
PHONE_PATTERN = re.compile(r"^\+?\d+$")

class BaseUser(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_first_name: Optional[Annotated[str, Field(max_length=100)]] = None
    user_last_name:  Optional[Annotated[str, Field(max_length=100)]] = None
    username:        Optional[Annotated[str, Field(max_length=100)]] = None
    email:           Optional[Annotated[EmailStr, Field(max_length=255)]] = None
    phone_number:    Optional[Annotated[str, Field(max_length=20)]] = None
    role_id:         Optional[Annotated[int, Field(ge=1)]] = None
    password:        Optional[Annotated[str, Field(min_length=8, max_length=100)]] = None

    @field_validator('user_first_name', 'user_last_name')
    def _validate_name(cls, v):
        if v is None:
            return None
        s = v.strip()
        if not (1 <= len(s) <= 100):
            raise ValueError('Doit contenir entre 1 et 100 caractères')
        if not NAME_PATTERN.match(s):
            raise ValueError("Caractères autorisés : lettres, espaces, apostrophes et tirets")
        return s

    @field_validator('username')
    def _validate_username(cls, v):
        if v is None:
            return None
        s = v.strip()
        if not (1 <= len(s) <= 100):
            raise ValueError("Nom d'utilisateur : longueur invalide (max 100)")
        if not USERNAME_PATTERN.match(s):
            raise ValueError("Nom d'utilisateur : uniquement lettres et chiffres")
        return s

    @field_validator('phone_number')
    def _validate_phone(cls, v):
        if v is None:
            return None
        s = v.strip()
        if not (1 <= len(s) <= 20):
            raise ValueError('Téléphone : longueur invalide (max 20)')
        if not PHONE_PATTERN.match(s):
            raise ValueError('Téléphone : uniquement chiffres et un préfixe + optionnel')
        return s

    @field_validator('password')
    def _validate_password(cls, v):
        if v is None:
            return None
        if not (8 <= len(v) <= 100):
            raise ValueError('Mot de passe : longueur invalide (8-100 caractères)')
        return v


class UserCreate(BaseUser):
    # rendre obligatoires les champs pour la création
    user_first_name: Annotated[str, Field(max_length=100)]
    user_last_name:  Annotated[str, Field(max_length=100)]
    username:        Annotated[str, Field(max_length=100)]
    email:           Annotated[EmailStr, Field(max_length=255)]
    phone_number:    Annotated[str, Field(max_length=20)]
    role_id:         Annotated[int, Field(ge=1)]
    password:        Annotated[str, Field(min_length=8, max_length=100)]


class UserUpdate(BaseUser):
    # héritage pur : tous les champs optionnels
    pass


__all__ = ["BaseUser", "UserCreate", "UserUpdate"]