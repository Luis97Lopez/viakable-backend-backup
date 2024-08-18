from functools import lru_cache
from pydantic import BaseModel, Json, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeploySettings(BaseModel):
    host: str = '0.0.0.0'
    port: int = 7000
    environment: str = 'dev'


class CORSSettings(BaseModel):
    allow: bool = True
    credentials: bool = True
    origins: Json[list[str]] = ['*', ]
    methods: Json[list[str]] = ['*', ]
    headers: Json[list[str]] = ['*', ]
    expose_headers: Json[list[str]] = ['*', ]


class DatabaseSettings(BaseModel):
    host: str = 'localhost'
    name: str = 'postgres'
    port: str = 5432
    user: str = 'postgres'
    password: str = 'postgres'


class JWTSettings(BaseModel):
    secret_access_token: str = 'verysecret'
    expiration_access_token: int = Field(default=1800, ge=0, le=10800)
    secret_refresh_token: str = 'verysecret'
    expiration_refresh_token: int = Field(default=86400, ge=0, le=2592000)


class AppSettings(BaseModel):
    super_user_username: str = 'SuperAdmin1'
    super_user_password: str = 'password'
    maximum_page_size: int = 100


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    cors: CORSSettings = CORSSettings()
    jwt: JWTSettings = JWTSettings()
    deploy: DeploySettings = DeploySettings()
    db: DatabaseSettings = DatabaseSettings()

    model_config = SettingsConfigDict(
        env_file='.env',
        env_nested_delimiter='__',
    )


# decorator to return always a cached value after the first real call to the method
#  as we do not want to load and read multiple time files, validate values etc...
#  see https://docs.python.org/3/library/functools.html#functools.lru_cache
@lru_cache
def get_settings():
    return Settings()
