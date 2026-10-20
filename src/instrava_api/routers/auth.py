from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from instrava_api.core.database import get_db
from instrava_api.schemas.user import UserPublic, UserRegister
from instrava_api.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário com nome, e-mail e senha (armazenada com Argon2id).",
)
async def register(
    payload: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublic:
    service = UserService(session=db)
    user = await service.register_user(payload)
    return UserPublic.model_validate(user)
