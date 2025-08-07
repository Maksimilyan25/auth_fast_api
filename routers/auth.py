import os
from datetime import datetime, timedelta, timezone

import jwt

from dotenv import load_dotenv

from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from passlib.context import CryptContext

from app.database.db import get_db
from app.models.users import User
from app.schemas import CreateUser, Token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
auth_router = APIRouter(prefix='/auth', tags=['Auth'])
security = HTTPBearer()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')


@auth_router.post(
        '/', summary='Создание пользователя',
        status_code=status.HTTP_201_CREATED)
async def create_user(
     db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser):
    await db.execute(insert(User).values(
        username=create_user.username,
        first_name=create_user.first_name,
        last_name=create_user.last_name,
        email=create_user.email,
        password=bcrypt_context.hash(create_user.password))
        )
    await db.commit()
    return {
        'detail': 'Пользователь создан',
        'status_code': status.HTTP_201_CREATED
    }


async def auth_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))

    if not user:
        raise HTTPException(
            detail='Неверные логин для аутентификации',
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if not bcrypt_context.verify(password, user.password):
        raise HTTPException(
            detail='Неверные пароль для аутентификации',
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return user


async def create_token(username: str, user_id: int, time: timedelta):
    payload = {
        'sub': username,
        'id': user_id,
        'exp': datetime.now(timezone.utc) + time
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@auth_router.post('/token', response_model=Token)
async def login(
     db: Annotated[AsyncSession, Depends(get_db)],
     form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await auth_user(db, form_data.username, form_data.password)
    token = await create_token(
        user.username, user.id, time=timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get('sub')
        user_id: int | None = payload.get('id')
        time: int | None = payload.get('exp')

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Не удалось проверить пользователя'
            )
        if time is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Токен доступа не предоставлен'
            )

        if not isinstance(time, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Неверный формат токена'
            )

        current_time = datetime.now(timezone.utc).timestamp()

        if time < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired!'
            )

        return {
            'username': username,
            'id': user_id,
        }
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Недействительный токен')
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Срок действия токена истек')
