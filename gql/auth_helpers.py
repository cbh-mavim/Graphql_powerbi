# gql/auth_helpers.py

from strawberry.types import Info
from fastapi import HTTPException
from typing import List, Optional
from auth import User  # Import your User class for type hinting

def get_user_from_context(info: Info) -> User:
    """Safely retrieves the user object from the GraphQL context."""
    user: Optional[User] = info.context.get("user")
    if not user:
        # This error should ideally not be reached if the GraphQLRouter dependency is set up
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def user_has_role(info: Info, required_roles: List[str]):
    """
    Checks if the user in the context has at least one of the required roles.
    Raises a 403 Forbidden HTTPException if the check fails.
    """
    user = get_user_from_context(info)
    if not any(role in user.roles for role in required_roles):
        raise HTTPException(
            status_code=403,
            detail=f"Forbidden: You need one of these roles to perform this action: {required_roles}"
        )

def user_has_scope(info: Info, required_scopes: List[str]):
    """
    Checks if the user's token in the context has all required scopes.
    Raises a 403 Forbidden HTTPException if the check fails.
    """
    user = get_user_from_context(info)
    if not user.scp:
        raise HTTPException(status_code=403, detail="Forbidden: No scopes present in the token.")
    
    token_scopes = user.scp.split()
    for scope in required_scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: Your token is missing the required '{scope}' scope."
            )