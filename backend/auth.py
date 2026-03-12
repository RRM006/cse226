from dataclasses import dataclass

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from backend.config import settings
from backend.database import get_profile

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@dataclass
class CurrentUser:
    id: str
    email: str
    role: str


_jwks = None


async def get_jwks():
    global _jwks
    if _jwks is None:
        url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            _jwks = response.json()
    return _jwks


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    try:
        # Validate JWT using JWKS
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        jwk_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                jwk_key = key
                break

        if not jwk_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        algorithms = [unverified_header.get("alg", "RS256")]

        payload = jwt.decode(
            token, jwk_key, algorithms=algorithms, audience="authenticated"
        )
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    profile = await get_profile(user_id)
    if not profile:
        role = "student"
    else:
        role = profile.get("role", "student")

    return CurrentUser(id=user_id, email=email, role=role)


async def require_admin(current_user: CurrentUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not an admin")
    return current_user
