import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.config import get_settings
from utils.logs import initialize_logs_service, get_logger
from db.init_db import init_db
from contextlib import asynccontextmanager
import asyncio

from api import routes, middlewares

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

app.middleware("http")(middlewares.error_handling_middleware)

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
app.include_router(routes.operators.router)
app.include_router(routes.admins.router)
app.include_router(routes.forklifts.router)
app.include_router(routes.materials.router)
app.include_router(routes.orders.router)


@app.get('/')
def home():
    return 'Viakable MiMaterial API'


if __name__ == '__main__':
    host = settings.deploy.host
    port = settings.deploy.port
    env = settings.deploy.environment

    # Trying to initialize DB
    if not asyncio.run(init_db()):
        raise RuntimeError("Could not initialize DB")

    if env == 'dev':
        uvicorn.run("main:app", host=host, port=port, reload=True)
    elif env == 'production':
        uvicorn.run("main:app", host=host, port=port)
    else:
        logger.error('No env set')
