import logging
from fastapi import Request, HTTPException
from jose import jwt, JWTError
import httpx  # type: ignore
from typing import Optional, List
from time import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Auth")

# --- CONFIGURATION ---
TENANT_ID = "74c129d6-75e9-47bc-89e7-fc64baa89a47"
CLIENT_ID = "3bd13b6a-2f23-4ace-9d71-d6d6a8e77a4e"
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
OPENID_CONFIG_URL = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"
ALGORITHMS = ["RS256"]

# --- POWER BI AUTH HEADER ---
AUTH_CHALLENGE_HEADER = {
    "WWW-Authenticate": f'Bearer authorization_uri="https://login.microsoftonline.com/{TENANT_ID}", resource_id="{CLIENT_ID}"'
}

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

# Global flag to ensure token is logged only once
token_logged = False


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
    global token_logged
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning("[Auth][WARN] Missing Authorization header. Sending 401 challenge.")
        raise HTTPException(status_code=401, detail="Authorization header is missing", headers=AUTH_CHALLENGE_HEADER)

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme. Must be 'Bearer'.", headers=AUTH_CHALLENGE_HEADER)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format.", headers=AUTH_CHALLENGE_HEADER)

    # 👇 Print token only once
    if not token_logged:
        logger.info(f"[Auth] Access Token (first request only): {token}")
        token_logged = True

    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = next((key for key in jwks["keys"] if key["kid"] == unverified_header.get("kid")), None)

        if not rsa_key:
            logger.error("[Auth][ERROR] No matching key ID (kid) found in JWKS.")
            raise HTTPException(status_code=401, detail="Unable to find a matching key to verify the token.", headers=AUTH_CHALLENGE_HEADER)

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
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}", headers=AUTH_CHALLENGE_HEADER)
    except Exception as e:
        logger.error("[Auth][ERROR] An unexpected error occurred during token verification: %s", e)
        raise HTTPException(status_code=500, detail="An error occurred during token verification.")
