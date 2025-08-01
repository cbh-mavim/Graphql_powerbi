import strawberry
from .query import Query

schema = strawberry.Schema(query=Query)

__all__ = ["schema"]