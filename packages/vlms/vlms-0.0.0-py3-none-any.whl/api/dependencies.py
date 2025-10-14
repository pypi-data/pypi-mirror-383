from fastapi import Header, HTTPException, status, Depends
from typing import Optional, Annotated
from config import get_admin_api_key


async def verify_admin_key(
    x_admin_api_key: Annotated[Optional[str], Header()] = None
) -> str:
    if not x_admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Admin-API-Key header required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if x_admin_api_key != get_admin_api_key():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key",
        )

    return x_admin_api_key


async def verify_gemini_key(
    x_gemini_api_key: Annotated[Optional[str], Header()] = None
) -> str:
    if not x_gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Gemini-API-Key header required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return x_gemini_api_key


class SecurityHeaders:
    def __init__(
        self,
        admin_key: Annotated[str, Depends(verify_admin_key)],
        gemini_key: Annotated[str, Depends(verify_gemini_key)]
    ):
        self.admin_key = admin_key
        self.gemini_key = gemini_key