# Авторизация на FastAPI.
Описание проекта
Ппроект представляет собой простую версию авторизации с использованием FastAPI.

# Стек технологий

1. **Backend**
   - Python 3.12
   - FastAPI: высокопроизводительный веб-фреймворк для быстрого написания RESTful API.
   - SQLAlchemy: библиотека Python для взаимодействия с базами данных.
   - PostgreSQL: реляционная база данных для хранения всех сущностей приложения.
   - OAuth2 и JWT: для реализации аутентификации и авторизации.

# Запуск:

1. Установка зависимостей - pip install -r requirements.txt
2. Создайте базу данных PostgreSQL и настройте подключение через .env файл.
3. Выполните миграцию базы данных:
4. alembic init -t async app/migrations
5. alembic revision --autogenerate -m "Initial migration"
6. alembic upgrade head
7. uvicorn app.main:app
8. Откройте приложение в браузере: http://localhost:8000/docs
9. Создание пользователя (create_user).
10. Получение токена(login).
11. Авторизация по username и password.
12. Проверка отправки запроса только для авторизованных пользователей.
