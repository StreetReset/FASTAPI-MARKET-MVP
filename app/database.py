#----------------SYNC----------------
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, DeclarativeBase
# DATABASE_URL = "sqlite:///ecommerce.db"

# engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal = sessionmaker(
#     autocommit = False,
#     autoflush= False,
#     bind = engine
# )

#----------------ASYNC----------------

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://ecommerce_user:sewjr3@localhost:5432/ecommerce_db"

async_engine = create_async_engine(DATABASE_URL, echo = True) #False для проды
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

