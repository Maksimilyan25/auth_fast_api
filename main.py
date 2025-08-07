from fastapi import FastAPI
from app.routers.users import users_router
from app.routers.auth import auth_router


app = FastAPI(title='MyFastAPI', description='Сервис авторизации')


@app.get('/', summary='Домашняя страница')
async def home_page():
    return {
        'message': 'Главная страница'
    }


app.include_router(users_router)
app.include_router(auth_router)
