
import strawberry
from strawberry.types import Info
from typing import List
from gql.auth_helpers import user_has_role # Import our new helper

# This defines how a User object will look in the GraphQL schema
@strawberry.type
class UserGQL:
    id: str
    name: str
    roles: List[str]

@strawberry.type
class Query:
    @strawberry.field
    def me(self, info: Info) -> UserGQL:
        """Returns the currently authenticated user's information."""
        user = info.context["user"]
        return UserGQL(id=user.id, name=user.name, roles=user.roles)

    @strawberry.field
    def public_data(self, info: Info) -> str:
        """An example of a field available to any authenticated user."""
        return "This is public data, available to all logged-in users."

    @strawberry.field
    def admin_only_data(self, info: Info) -> str:
        """An example of a field that requires the 'Admin' role."""
        # This one line protects the entire resolver.
        user_has_role(info, required_roles=["Admin"])
        
        # The rest of the function only runs if the check passes.
        return "This is top secret admin data!"

    @strawberry.field
    def editor_data(self, info: Info) -> str:
        """An example of a field requiring one of several roles."""
        user_has_role(info, required_roles=["Admin", "Editor"])

        user = info.context["user"]
        return f"This data can be accessed by editors and admins. You are: {user.name}"