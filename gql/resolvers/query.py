import strawberry
from strawberry.types import Info
from typing import List
from main import CustomContext

@strawberry.type
class UserType:
    id: str
    username: str
    roles: List[str]


@strawberry.type
class Query:
    @strawberry.field
    def me(self, info: Info[CustomContext, None]) -> UserType:
        """
        Returns the currently authenticated user's information.
        """
        user = info.context.user
        
        # The context getter already ensures a user exists, but an extra check is good practice.
        if not user:
            raise Exception("Authentication required!")
            
        return UserType(id=user.id, username=user.username, roles=user.roles)

    @strawberry.field
    def admin_only_data(self, info: Info[CustomContext, None]) -> str:
        """
        An example of a field that requires a specific role.
        """
        user = info.context.user

        if not user:
            raise Exception("Authentication required!")
        
        if "admin" not in user.roles:
            raise Exception("You do not have permission to access this resource.")
            
        return "This is top secret admin data!"