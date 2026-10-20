from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from instrava_api.core.security import verify_password
from instrava_api.models.user import User


@pytest.mark.asyncio
async def test_ac01_register_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """AC-01: Payload válido, e-mail novo -> 201; body contém id, name, email, created_at; sem password / password_hash."""
    payload = {
        "name": " Maria Silva ",
        "email": "maria@example.com",
        "password": "senha-secreta",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["name"] == "Maria Silva"
    assert data["email"] == "maria@example.com"
    assert "created_at" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_ac02_register_duplicate_email(client: AsyncClient) -> None:
    """AC-02: Mesmo e-mail duas vezes -> segundo request 409 com EMAIL_ALREADY_REGISTERED."""
    payload = {
        "name": "Maria Silva",
        "email": "maria@example.com",
        "password": "senha-secreta",
    }
    first_response = await client.post("/api/v1/auth/register", json=payload)
    assert first_response.status_code == 201

    second_response = await client.post("/api/v1/auth/register", json=payload)
    assert second_response.status_code == 409

    data = second_response.json()
    assert data == {
        "detail": {
            "code": "EMAIL_ALREADY_REGISTERED",
            "message": "E-mail já cadastrado.",
        }
    }


@pytest.mark.asyncio
async def test_ac03_register_case_insensitive_email(client: AsyncClient) -> None:
    """AC-03: E-mail existente com caixa diferente (Maria@example.com vs maria@example.com) -> 409."""
    payload1 = {
        "name": "Maria Silva",
        "email": "Maria@example.com",
        "password": "senha-secreta",
    }
    res1 = await client.post("/api/v1/auth/register", json=payload1)
    assert res1.status_code == 201
    assert res1.json()["email"] == "maria@example.com"

    payload2 = {
        "name": "Outra Maria",
        "email": "  mArIa@example.com  ",
        "password": "outra-senha-123",
    }
    res2 = await client.post("/api/v1/auth/register", json=payload2)
    assert res2.status_code == 409
    assert res2.json()["detail"]["code"] == "EMAIL_ALREADY_REGISTERED"


@pytest.mark.asyncio
async def test_ac04_register_invalid_email(client: AsyncClient) -> None:
    """AC-04: E-mail inválido -> 422."""
    payload = {
        "name": "Maria Silva",
        "email": "invalid-email-string",
        "password": "senha-secreta",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ac05_register_password_length(client: AsyncClient) -> None:
    """AC-05: Senha com menos de 8 caracteres -> 422 (e mais de 16 -> 422)."""
    # Menos de 8 caracteres
    payload_short = {
        "name": "Maria Silva",
        "email": "maria@example.com",
        "password": "short",
    }
    res_short = await client.post("/api/v1/auth/register", json=payload_short)
    assert res_short.status_code == 422

    # Mais de 16 caracteres
    payload_long = {
        "name": "Maria Silva",
        "email": "maria@example.com",
        "password": "this-password-is-way-too-long",
    }
    res_long = await client.post("/api/v1/auth/register", json=payload_long)
    assert res_long.status_code == 422


@pytest.mark.asyncio
async def test_ac06_register_missing_fields(client: AsyncClient) -> None:
    """AC-06: Campo obrigatório ausente -> 422."""
    # Ausência de name
    res1 = await client.post(
        "/api/v1/auth/register",
        json={"email": "maria@example.com", "password": "senha-secreta"},
    )
    assert res1.status_code == 422

    # Ausência de email
    res2 = await client.post(
        "/api/v1/auth/register",
        json={"name": "Maria", "password": "senha-secreta"},
    )
    assert res2.status_code == 422

    # Ausência de password
    res3 = await client.post(
        "/api/v1/auth/register",
        json={"name": "Maria", "email": "maria@example.com"},
    )
    assert res3.status_code == 422

    # Nome vazio ou só espaços
    res4 = await client.post(
        "/api/v1/auth/register",
        json={"name": "   ", "email": "maria@example.com", "password": "senha-secreta"},
    )
    assert res4.status_code == 422


@pytest.mark.asyncio
async def test_ac07_password_hash_verification(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """AC-07: Após 201, registro no banco tem password_hash diferente do plaintext e verificável com Argon2id."""
    raw_password = "senha-secreta"
    payload = {
        "name": "Maria Silva",
        "email": "maria@example.com",
        "password": raw_password,
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    # Busca usuário persistido no banco
    stmt = select(User).where(User.email == "maria@example.com")
    result = await db_session.execute(stmt)
    user = result.scalars().first()

    assert user is not None
    assert user.password_hash != raw_password
    assert "$argon2" in user.password_hash
    assert verify_password(raw_password, user.password_hash) is True
    assert verify_password("wrong-password", user.password_hash) is False


@pytest.mark.asyncio
async def test_race_condition_integrity_error_mapped_to_409(
    client: AsyncClient,
) -> None:
    """Conflito de unique constraint por condição de corrida no create deve mapear para 409."""
    payload = {
        "name": "Maria Silva",
        "email": "maria_race@example.com",
        "password": "senha-secreta",
    }
    with patch(
        "instrava_api.repositories.user_repository.UserRepository.create",
        side_effect=IntegrityError("statement", "params", "orig"),
    ):
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409
        assert response.json() == {
            "detail": {
                "code": "EMAIL_ALREADY_REGISTERED",
                "message": "E-mail já cadastrado.",
            }
        }


@pytest.mark.asyncio
async def test_unexpected_error_returns_500_without_internal_details(
    client: AsyncClient,
) -> None:
    """RNF-05: Falhas inesperadas respondem 500 sem detalhe interno."""
    payload = {
        "name": "Maria Silva",
        "email": "maria_err@example.com",
        "password": "senha-secreta",
    }
    with patch(
        "instrava_api.services.user_service.UserService.register_user",
        side_effect=RuntimeError("Secret database connection string leaked"),
    ):
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 500
        data = response.json()
        assert data == {"detail": "Internal server error"}
        assert "Secret" not in response.text
