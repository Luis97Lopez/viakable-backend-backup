from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.config import get_settings


settings = get_settings()


SQLALCHEMY_DATABASE_URL: str = f"postgresql://{settings.db.user}:{settings.db.password}" \
                          f"@{settings.db.host}:{settings.db.port}/{settings.db.name}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
