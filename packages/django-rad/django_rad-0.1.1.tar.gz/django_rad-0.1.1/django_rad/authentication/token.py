from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
from .base import BaseAuthentication
import datetime

User = get_user_model()


JWT_SECRET = getattr(settings, "SECRET_KEY", "supersecret")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600
JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXP = 3600  # 1 hour
REFRESH_TOKEN_EXP = 60 * 60 * 24 * 7  # 7 days


User = get_user_model()


class JWTTokenAuthentication(BaseAuthentication):
    """
    Usage: Add to ApiController.authentication_classes
    Authorization: Bearer <key>
    """

    requires_csrf = False

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            request.user = None
            return None

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            request.user = None
            return None
        except jwt.InvalidTokenError:
            request.user = None
            return None

        try:
            user = User.objects.get(id=payload["user_id"])
            request.user = user
        except User.DoesNotExist:
            return None

        request._dont_enforce_csrf_checks = True
        return user


def create_jwt_pair(user, extra: dict | None = None):
    """
    Return a (access_token, refresh_token) pair for the given user.
    """
    now = datetime.datetime.now()

    access_payload = {
        "type": "access",
        "user_id": user.id,
        "username": user.username,
        "exp": now + datetime.timedelta(seconds=ACCESS_TOKEN_EXP),
        "iat": now,
    }
    refresh_payload = {
        "type": "refresh",
        "user_id": user.id,
        "username": user.username,
        "exp": now + datetime.timedelta(seconds=REFRESH_TOKEN_EXP),
        "iat": now,
    }

    if extra:
        access_payload.update(extra)
        refresh_payload.update(extra)

    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return access_token, refresh_token


def decode_jwt(token: str):
    """Validate and decode a JWT. Raises jwt exceptions if invalid."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def refresh_jwt_pair(refresh_token: str):
    """
    Given a valid refresh token, return a new (access, refresh) pair.
    Retains the original 'extra' data.
    """
    try:
        payload = decode_jwt(refresh_token)
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid refresh token")

    if payload.get("type") != "refresh":
        raise ValueError("Not a refresh token")

    # Get user
    try:
        user = User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        raise ValueError("User not found")

    # Preserve any extra data (exclude reserved fields)
    reserved_keys = {"type", "user_id", "username", "exp", "iat"}
    extra = {k: v for k, v in payload.items() if k not in reserved_keys}

    return create_jwt_pair(user, extra)
