import logging
from fastapi import Request, HTTPException
from jose import jwt, JWTError
import httpx  # type: ignore
from typing import Optional, Dict, Any, List
from time import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Auth")

# Azure AD and app-specific configuration
TENANT_ID = "74c129d6-75e9-47bc-89e7-fc64baa89a47"
CLIENT_ID = "api://d9f4027b-8e17-4831-9f24-13edd254c47d"
ISSUER = f"https://sts.windows.net/{TENANT_ID}/"
OPENID_CONFIG_URL = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"
ALGORITHMS = ["RS256"]

# User class
class User:
    def __init__(self, id: str, name: Optional[str] = None, roles: Optional[List[str]] = None, scp: Optional[str] = None):
        self.id = id
        self.name = name
        self.roles = roles or []
        self.scp = scp

# JWKS caching setup
jwks_cache = {
    "keys": None,
    "expiry": 0
}
CACHE_LIFETIME_SECONDS = 3600

# Fetch JWKS from Azure or return cached keys
async def get_jwks():
    global jwks_cache
    current_time = time()

    if jwks_cache["keys"] and jwks_cache["expiry"] > current_time:
        logger.info("[Auth] Using cached JWKS.")
        return jwks_cache["keys"]

    logger.info("[Auth] Fetching new JWKS from: %s", OPENID_CONFIG_URL)
    async with httpx.AsyncClient() as client:
        try:
            oidc_res = await client.get(OPENID_CONFIG_URL)
            oidc_res.raise_for_status()
            oidc_config = oidc_res.json()
            jwks_uri = oidc_config["jwks_uri"]

            jwks_res = await client.get(jwks_uri)
            jwks_res.raise_for_status()
            jwks = jwks_res.json()

            jwks_cache["keys"] = jwks
            jwks_cache["expiry"] = current_time + CACHE_LIFETIME_SECONDS
            logger.info("[Auth] Successfully fetched and cached new JWKS.")
            return jwks

        except httpx.HTTPError as e:
            logger.error("[Auth][ERROR] Failed to fetch OpenID config or JWKS: %s", e)
            raise HTTPException(status_code=500, detail="Could not fetch security keys for authentication.")

# Main token verification function
async def verify_token(request: Request) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning("[Auth][WARN] Missing Authorization header.")
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme. Must be 'Bearer'.")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format.")

    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = next((key for key in jwks["keys"] if key["kid"] == unverified_header.get("kid")), None)

        if not rsa_key:
            logger.error("[Auth][ERROR] No matching key ID (kid) found in JWKS.")
            raise HTTPException(status_code=401, detail="Unable to find a matching key to verify the token.")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=CLIENT_ID,
            issuer=ISSUER,
        )

        user = User(
            id=payload.get("oid"),
            name=payload.get("name"),
            roles=payload.get("roles"),
            scp=payload.get("scp")
        )

        logger.info("[Auth] Token successfully verified for user ID: %s", user.id)
        return user

    except JWTError as e:
        logger.error("[Auth][ERROR] Token validation failed: %s", e)
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except Exception as e:
        logger.error("[Auth][ERROR] An unexpected error occurred during token verification: %s", e)
        raise HTTPException(status_code=500, detail="An error occurred during token verification.")
