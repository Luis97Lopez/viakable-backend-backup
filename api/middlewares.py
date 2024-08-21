import traceback

from fastapi import Request, status
from fastapi.responses import JSONResponse
from utils.logs import get_logger


logger = get_logger(__name__)


async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Server error {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"message": "Server Error, please try again later."})
