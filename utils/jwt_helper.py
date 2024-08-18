import time
import jwt
from utils.config import get_settings


settings = get_settings()

ACCESS_TOKEN_DURATION_SECONDS = settings.jwt.expiration_access_token
SECRET_KEY_ACCESS_TOKEN = settings.jwt.secret_access_token
REFRESH_TOKEN_DURATION_SECONDS = settings.jwt.expiration_refresh_token
SECRET_KEY_REFRESH_TOKEN = settings.jwt.secret_refresh_token


def encode_access_token(user_id) -> tuple[str, float]:
    """
    Encode an access token JWT with the user_id and an expiration date.

    Args:
        user_id (str): The user's ID.

    Returns:
        str: The encoded access token.
    """
    expires_at = time.time() + ACCESS_TOKEN_DURATION_SECONDS
    payload = {
        "sub": user_id,
        "exp": expires_at
    }
    token = jwt.encode(payload, SECRET_KEY_ACCESS_TOKEN, algorithm='HS256')
    return token, expires_at


def encode_refresh_token(user_id) -> tuple[str, float]:
    """
    Encode a refresh token JWT with the user_id and an expiration date.

    Args:
        user_id (str): The user's ID.

    Returns:
        str: The encoded refresh token.
    """
    expires_at = time.time() + REFRESH_TOKEN_DURATION_SECONDS
    payload = {
        "sub": user_id,
        "exp": expires_at
    }
    token = jwt.encode(payload, SECRET_KEY_REFRESH_TOKEN, algorithm='HS256')
    return token, expires_at


def decode_access_token(token):
    """
    Decode an access token and verify its signature and expiration date.

    Args:
        token (str): The access token to decode.

    Returns:
        dict: The content of the access token if it's valid and hasn't expired, or None if the access token is invalid
        or has expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY_ACCESS_TOKEN, algorithms=['HS256'])
        current_time = time.time()
        if 'exp' in payload and payload['exp'] > current_time:
            return payload
        else:
            return None
    except jwt.ExpiredSignatureError:
        # The access token has expired
        return None
    except jwt.PyJWTError:
        # The access token is not valid
        return None


def decode_refresh_token(token):
    """
    Decode a refresh token and verify its signature and expiration date.

    Args:
        token (str): The refresh token to decode.

    Returns:
        dict: The content of the refresh token if it's valid and hasn't expired, or None if the refresh token is invalid
        or has expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY_REFRESH_TOKEN, algorithms=['HS256'])
        current_time = time.time()
        if 'exp' in payload and payload['exp'] > current_time:
            return payload
        else:
            return None
    except jwt.ExpiredSignatureError:
        # The refresh token has expired
        return None
    except jwt.PyJWTError:
        # The refresh token is not valid
        return None
