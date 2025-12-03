from typing import Optional, Annotated
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, ValidationError



class EventBase(BaseModel):
    """Schéma de base pour les événements.
    Pattern utilisé :
    - `EventBase` : champs optionnels + validateurs
    - `EventCreate` : champs requis pour la création
    - `EventUpdate` : tous les champs optionnels pour les mises à jour
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    contract_id: Optional[Annotated[int, Field(ge=1)]] = None
    customer_id: Optional[Annotated[int, Field(ge=1)]] = None
    user_support_id: Optional[Annotated[int, Field(ge=1)]] = None
    event_name: Optional[Annotated[str, Field(max_length=255)]] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    location: Optional[Annotated[str, Field(max_length=500)]] = None
    attendees: Optional[Annotated[int, Field(ge=0)]] = None
    note: Optional[Annotated[str, Field(max_length=2000)]] = None

    @field_validator('event_name')
    def _validate_name(cls, v):
        if v is None:
            return None
        s = v.strip()
        if not (1 <= len(s) <= 255):
            raise ValueError('Le nom de l\'événement doit contenir entre 1 et 255 caractères')
        return s
    
    @model_validator(mode='after')
    def _check_dates(self):

        if self.start_datetime and self.end_datetime:
            if self.start_datetime < datetime.now() or self.end_datetime < datetime.now():
                raise ValueError('Les dates d\'événement doivent être dans le futur')
            if self.end_datetime < self.start_datetime:
                raise ValueError('La date de fin doit être postérieure ou égale à la date de début')
        return self

    @field_validator('attendees')
    def _validate_attendees(cls, v):
        if v is None:
            return None
        if v < 0:
            raise ValueError('Le nombre de participants ne peut pas être négatif')
        return v


class EventCreate(EventBase):
    contract_id: Annotated[int, Field(ge=1)]
    customer_id: Annotated[int, Field(ge=1)]
    event_name: Annotated[str, Field(max_length=255)]



class EventUpdate(EventBase):
    # all fields optional for partial updates
    pass


__all__ = ["EventBase", "EventCreate", "EventUpdate", "ValidationError"]
