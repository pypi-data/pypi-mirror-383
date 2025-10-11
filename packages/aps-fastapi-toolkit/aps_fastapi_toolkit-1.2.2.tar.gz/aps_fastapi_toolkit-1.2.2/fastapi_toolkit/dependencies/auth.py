from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from typing import Any

from .user import UserServiceDependency
from fastapi_toolkit.utils import CookieNames
from fastapi_toolkit.services import JWTService, CookieService

# -------------------- OAuth2 Scheme Dependency -------------------- #

_token_url = None
_oauth2_scheme = None


def set_token_url(url: str):
    """
    Set the token URL for OAuth2PasswordBearer.
    """
    global _token_url, _oauth2_scheme
    _token_url = url
    _oauth2_scheme = OAuth2PasswordBearer(tokenUrl=_token_url, auto_error=False)


def _get_oauth2_scheme() -> OAuth2PasswordBearer:
    if not _token_url or _oauth2_scheme is None:
        raise RuntimeError("Token URL is not set. Call `set_token_url()` first.")
    return _oauth2_scheme


# -------------------- JWT Service Dependency -------------------- #
_jwt_service = None


def init_jwt_service(service: JWTService):
    """
    Initialize the JWT service.
    """
    global _jwt_service
    _jwt_service = service


async def _get_jwt_service() -> JWTService:
    """
    Returns the JWT service instance.
    """
    if _jwt_service is None:
        raise RuntimeError(
            "JWT service is not initialized. "
            "Call `init_jwt_service()` during startup."
        )
    return _jwt_service


JWTServiceDependency = Annotated[JWTService, Depends(_get_jwt_service)]


# -------------------- Cookie Service Dependency -------------------- #


async def _get_cookie_service(jwt_service: JWTServiceDependency) -> CookieService:
    """
    Returns the Cookie service instance.
    """
    return CookieService(
        jwt_service.access_token_lifetime, jwt_service.refresh_token_lifetime
    )


CookieServiceDependency = Annotated[CookieService, Depends(_get_cookie_service)]


# -------------------- Auth Dependency -------------------- #


async def _get_user(
    token: str | None,
    jwt_service: JWTServiceDependency,
    user_service: UserServiceDependency,
):
    """
    Returns the currently authenticated user based on the token.
    """
    if not token:
        return None

    payload = jwt_service.decode_token(token)
    if payload.type != "access":
        return None

    email = payload.data.get("email")
    return user_service.get_user_by_email(email) if email else None


def _get_auth_dependency(from_cookie: bool):
    async def _dependency(
        request: Request,
        jwt_service: JWTServiceDependency,
        user_service: UserServiceDependency,
        token: Annotated[str | None, Depends(_get_oauth2_scheme)] = None,
    ):
        token = request.cookies.get(CookieNames.ACCESS.value) if from_cookie else token
        return await _get_user(
            token,
            jwt_service,
            user_service,
        )

    return _dependency


async def _is_user_authenticated(user: Any):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login to continue.",
        )
    return user


async def _is_anonymous(user: Any):
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already logged in.",
        )
    return None


_get_current_authenticated_user_cookie = _get_auth_dependency(from_cookie=True)
_get_current_authenticated_user = _get_auth_dependency(from_cookie=False)


async def is_authenticated_cookie(
    user: Annotated[Any, Depends(_get_current_authenticated_user_cookie)],
):
    """
    Dependency to check if the user is authenticated (using cookies).
    """
    return await _is_user_authenticated(user)


async def is_anonymous_cookie(
    user: Annotated[Any, Depends(_get_current_authenticated_user_cookie)],
):
    """
    Dependency to check if the user is anonymous (using cookies).
    """
    return await _is_anonymous(user)


async def is_authenticated_header(
    user: Annotated[Any, Depends(_get_current_authenticated_user)],
):
    """
    Dependency to check if the user is authenticated (using Headers).
    """
    return await _is_user_authenticated(user)


async def is_anonymous_header(
    user: Annotated[Any, Depends(_get_current_authenticated_user)],
):
    """
    Dependency to check if the user is anonymous (using headers).
    """
    return await _is_anonymous(user)
