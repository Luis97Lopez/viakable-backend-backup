from fastapi import Request, HTTPException, status
from utils.logs import get_logger


logger = get_logger(__name__)


async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Server error {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Server Error, please try again later.")
