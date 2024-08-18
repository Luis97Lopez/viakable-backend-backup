import logging

from db.base import SessionLocal

logger = logging.getLogger(__name__)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        logger.debug('Database Session opened.')
        yield db
    finally:
        logger.debug('Database Session closed.')
        db.close()
