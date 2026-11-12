from pydantic import BaseModel, Field
from decimal import Decimal


class ArticoloCreate(BaseModel):
    codice: str = Field(min_length=1, max_length=30)
    nome: str = Field(min_length=1, max_length=100)
    prezzo: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    scorta_minima: int = Field(ge=0)