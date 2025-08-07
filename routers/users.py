from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.db import get_db
from app.models.users import User
from app.routers.auth import get_current_user

users_router = APIRouter(prefix='/users', tags=['Пользователи'])


@users_router.get('/', summary='Список пользователей')
async def list_users(
     db: Annotated[AsyncSession, Depends(get_db)],
     token: dict = Depends(get_current_user)):
    users = await db.scalars(select(User))
    all_users = users.all()
    if not all_users:
        raise HTTPException(
            detail='Список пользователей пуст',
            status_code=status.HTTP_404_NOT_FOUND)
    return all_users


@users_router.delete('/{user_id}', summary='Удаление пользователя')
async def delete_user(
     db: Annotated[AsyncSession, Depends(get_db)],
     user_id: int,
     token: dict = Depends(get_current_user)):
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            detail='Пользователь не найден',
            status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(user)
    await db.commit()
    return {
        'detail': 'Пользователь удален',
        'status_code': status.HTTP_200_OK
    }
