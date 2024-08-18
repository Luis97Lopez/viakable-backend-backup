import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.config import get_settings
from utils.logs import initialize_logs_service, get_logger
from db.init_db import init_db
from contextlib import asynccontextmanager

from api import routes

# Logs service
initialize_logs_service()
logger = get_logger(__name__)

# Settings service
settings = get_settings()


@asynccontextmanager
async def lifespan(app_: FastAPI):
    logger.info(f'VIAKABLE BACKEND server ready and running.')
    while True:
        # Trying to initialize DB
        if await init_db():
            break
    logger.info(f'Everything\'s fine starting server')
    yield
    logger.info('Shutting down VIAKABLE BACKEND Server.')


app = FastAPI(lifespan=lifespan)


# CORS config
if settings.cors.allow:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins,
        allow_credentials=settings.cors.credentials,
        allow_methods=settings.cors.methods,
        allow_headers=settings.cors.headers,
        expose_headers=settings.cors.expose_headers,
    )

# Consumer route added
app.include_router(routes.auth.router)
app.include_router(routes.users.router)
# app.include_router(routes.teachers.router)
app.include_router(routes.admins.router)
# app.include_router(routes.schedules.router)
# app.include_router(routes.classes.router)
# app.include_router(routes.promotions.router)
# app.include_router(routes.purchases.router)
# app.include_router(routes.class_registers.router)


@app.get('/')
def home():
    return 'Viakable MiMaterial API'


if __name__ == '__main__':
    host = settings.app.host
    port = settings.app.port
    env = settings.app.environment

    if env == 'dev':
        uvicorn.run("main:app", host=host, port=port, reload=True)
    elif env == 'production':
        uvicorn.run("main:app", host=host, port=port)
    else:
        logger.error('No env set')
