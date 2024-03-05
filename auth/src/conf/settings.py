from pathlib import Path

from pydantic import BaseModel
from pydantic import DirectoryPath
from pydantic import Field
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class AlembicSettings(BaseModel):
    config: str = 'auth/src/alembic/alembic.ini'
    directory: str = 'auth/src/alembic'


class Settings(BaseSettings):
    DEBUG: bool = False

    BASE_DIR: DirectoryPath = Path.cwd()

    SECRETS: bool

    SECRET_KEY: str
    CRYPT_CONTEXT_SCHEMA: str = 'sha256_crypt'
    JWT_ALGORITHM: str = 'HS256'

    AUTH_EXCLUDE_URL_PREFIX: list[str] = [
        '/v1/auth/login/',
        '/v1/auth/signup/',
        '/v1/oauth/grant_access/',
        '/v1/oauth/user_info/',
    ]

    DATABASE_URL: PostgresDsn

    alembic: AlembicSettings = Field(default_factory=AlembicSettings)


settings = Settings()
