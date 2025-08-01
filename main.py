import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from strawberry.asgi import GraphQL
from fastapi.middleware.cors import CORSMiddleware
from gql.schemas import schema
from typing import Optional , Any
from auth import verify_token, User


class CustomContext:
    def __init__(self, request: Request, user: Optional[User] = None):
        self.request = request
        self.user = user


class MyGraphQLApp(GraphQL):
    async def get_context(self, request: Request, response: Any = None) -> CustomContext:
        if "text/html" in request.headers.get("accept", ""):
            return CustomContext(request=request)

        try:
            user = await verify_token(request)
            return CustomContext(request=request, user=user)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during GraphQL context creation: {e}")


app = FastAPI(title="Azure GraphQL Platform Processor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_app = MyGraphQLApp(schema)
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)

@app.get("/")
async def root():
    return {"message": "Welcome to Azure GraphQL Platform Processor", "graphql_endpoint": "/graphql"}


@app.get("/api/protected")
async def protected_route(user: User = Depends(verify_token)):
    return {
        "message": "You have access to the protected REST API!",
        "user": {"id": user.id, "name": user.name, "roles": user.roles, "scopes": user.scp}
    }


def main():
    print("Starting GraphQL server...")
    uvicorn.run('main:app', host='0.0.0.0', port=8000)

if __name__ == "__main__":
    main()
