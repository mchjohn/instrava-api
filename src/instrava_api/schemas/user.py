from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    name: str = Field(..., description="Nome de exibição do usuário (1-100 caracteres)")
    email: EmailStr = Field(..., max_length=255, description="E-mail único do usuário")
    password: str = Field(
        ..., min_length=8, max_length=16, description="Senha com 8 a 16 caracteres"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("O nome não pode ser vazio ou conter apenas espaços.")
        if len(trimmed) > 100:
            raise ValueError("O nome deve ter no máximo 100 caracteres.")
        return trimmed

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    created_at: datetime
