from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass

from auth.src.conf import settings

engine = create_async_engine(
    settings.DATABASE_URL.unicode_string(),
    pool_recycle=900,
    pool_size=100,
    max_overflow=3,
)

session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(MappedAsDataclass, DeclarativeBase):
    pass
