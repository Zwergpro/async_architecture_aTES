from pathlib import Path

from pydantic import BaseModel
from pydantic import DirectoryPath
from pydantic import Field
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class AlembicSettings(BaseModel):
    config: str = 'task_tracker/src/alembic/alembic.ini'
    directory: str = 'task_tracker/src/alembic'


class OAuthSettings(BaseModel):
    SERVICE_URL: str = 'http://127.0.0.1:8010/v1/oauth/grant_access/'
    SERVICE_USER_INFO_URL: str = 'http://auth:8010/v1/oauth/user_info/'
    CLIENT_ID: str = 'DEQU5'
    CLIENT_SECRET: str = '0LN801CZAY'


class Settings(BaseSettings):
    DEBUG: bool = False

    BASE_DIR: DirectoryPath = Path.cwd()

    SECRETS: bool

    SECRET_KEY: str
    CRYPT_CONTEXT_SCHEMA: str = 'sha256_crypt'
    JWT_ALGORITHM: str = 'HS256'

    AUTH_EXCLUDE_URL_PREFIX: list[str] = [
        '/v1/oauth/',
    ]

    DATABASE_URL: PostgresDsn

    alembic: AlembicSettings = Field(default_factory=AlembicSettings)
    oauth: OAuthSettings = Field(default_factory=OAuthSettings)


settings = Settings()
