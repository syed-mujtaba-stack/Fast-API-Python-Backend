from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from jose.utils import base64url_decode
import json
import httpx
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize HTTPBearer for token extraction
security = HTTPBearer()

# Clerk Configuration
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_API_URL = os.getenv("CLERK_API_URL", "https://api.clerk.dev")
CLERK_JWKS_URL = f"{CLERK_API_URL}/v1/jwks"

# Cache for JWKS
jwks_cache = None

async def get_jwks():
    """Fetch JWKS from Clerk"""
    global jwks_cache
    if not jwks_cache:
        async with httpx.AsyncClient() as client:
            response = await client.get(CLERK_JWKS_URL)
            response.raise_for_status()
            jwks_cache = response.json()
    return jwks_cache

def get_public_key(jwks: dict, token: str) -> str:
    """Get the public key from JWKS for the given token"""
    try:
        header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key["kid"] == header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        return rsa_key
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current user from JWT token"""
    token = credentials.credentials
    
    try:
        # Get JWKS
        jwks = await get_jwks()
        
        # Get public key
        public_key = get_public_key(jwks, token)
        
        if not public_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decode token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=CLERK_PUBLISHABLE_KEY,
            options={"verify_aud": True, "verify_iss": False},
        )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency for protected routes
async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Dependency to check if user is active"""
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
