# Market API (MVP)

Минимальный backend интернет-магазина на **FastAPI**.  
Проект является pet-project и реализует базовый функционал e-commerce API.

---

##  Стек технологий

- FastAPI
- SQLAlchemy 2.0
- PostgreSQL / SQLite
- Alembic
- Pydantic v2
- JWT (PyJWT)
- Uvicorn
- asyncpg / psycopg

---

##  Структура проекта
```
app/
├── models/ # SQLAlchemy модели
├── routers/ # Роуты (users, products, categories, auth)
├── migrations/ # Alembic миграции
├── config.py # Конфигурация
├── database.py # Подключение к БД
├── db_depends.py # Dependency для БД
├── schemas.py # Pydantic схемы
├── pagination.py # Пагинация
├── main.py # Точка входа
```
---

##  Установка

### 1. Клонирование
```bash
git clone https://github.com/StreetReset/FASTAPI-MARKET-MVP.git
cd FASTAPI-MARKET-MVP
```
---

## Особенности

- Асинхронная работа с БД (async SQLAlchemy + asyncpg)
- Чистая структура проекта (routers / models / schemas / dependencies)
- Использование SQLAlchemy 2.0 
- Валидация данных через Pydantic v2
- JWT авторизация
- Миграции через Alembic
- Разделение конфигурации через .env
- Готовая база для масштабирования проекта

---

## Планы

- Реализовать фильтрацию и поиск товаров
- Добавить загрузку изображений товаров
- Внедрить Redis для кэширования
- Docker + docker-compose
- Логирование и мониторинг
- Покрытие тестами (pytest)
- CI/CD (GitHub Actions)
