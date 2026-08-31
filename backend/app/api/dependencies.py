from fastapi import Header, HTTPException, status
from app.core.config import settings

async def verify_api_token(authorization: str = Header(None)):
    if not settings.API_SECRET_TOKEN:
        return True
        
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization ausente"
        )
        
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != settings.API_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de autenticacao invalido"
        )
    return True
