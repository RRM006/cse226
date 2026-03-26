import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config import settings
from database import create_profile, get_profile, get_student_by_student_id, update_profile_role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

STUDENT_JWT_SECRET = os.getenv("STUDENT_JWT_SECRET", "student-jwt-secret-change-in-production")
STUDENT_JWT_ALGORITHM = "HS256"
STUDENT_JWT_EXPIRE_MINUTES = 480  # 8 hours


@dataclass
class CurrentUser:
    id: str
    email: str
    role: str


@dataclass
class CurrentStudent:
    id: str
    student_id: str
    name: str
    role: str = "student"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(10)).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_student_token(student_id: str, student_db_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=STUDENT_JWT_EXPIRE_MINUTES)
    payload = {
        "sub": student_db_id,
        "student_id": student_id,
        "role": "student",
        "exp": expire,
    }
    return jwt.encode(payload, STUDENT_JWT_SECRET, algorithm=STUDENT_JWT_ALGORITHM)


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
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Check if this is a student token first
        try:
            student_payload = jwt.decode(
                token, STUDENT_JWT_SECRET, algorithms=[STUDENT_JWT_ALGORITHM]
            )
            if student_payload.get("role") == "student":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )
        except JWTError:
            pass

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

        if not email or not email.strip().lower().endswith("@northsouth.edu"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only @northsouth.edu accounts are allowed",
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
        profile = await create_profile(user_id, email, "admin")
        role = "admin"
    else:
        role = profile.get("role", "admin")
        if role != "admin":
            await update_profile_role(user_id, "admin")
            role = "admin"

    return CurrentUser(id=user_id, email=email, role=role)


async def require_admin(current_user: CurrentUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not an admin")
    return current_user


async def get_current_student(token: str = Depends(oauth2_scheme)) -> CurrentStudent:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            token, STUDENT_JWT_SECRET, algorithms=[STUDENT_JWT_ALGORITHM]
        )
        if payload.get("role") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student access required",
            )
        student_id = payload.get("student_id")
        db_id = payload.get("sub")
        if not student_id or not db_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        student = await get_student_by_student_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )
        return CurrentStudent(
            id=student["id"],
            student_id=student["student_id"],
            name=student.get("name", ""),
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_student(current_student: CurrentStudent = Depends(get_current_student)):
    if current_student.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    return current_student
