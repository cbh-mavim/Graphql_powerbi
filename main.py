# main.py

import uvicorn
import strawberry
from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware

# Import all necessary components from your other files
from auth import verify_token, User, require_role
from gql.resolvers.query_first import Query


schema = strawberry.Schema(query=Query) 

# This context_getter runs for every GraphQL request
async def get_context(user: User = Depends(verify_token)):
    """
    Verifies the token using the dependency and places the User object
    into the GraphQL context for use in resolvers.
    """
    return {"user": user}

# --- FASTAPI APP SETUP ---
app = FastAPI(title="Scalable GraphQL API with Azure AD")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GRAPHQL ROUTER ---
# The context_getter ensures every request to /graphql is authenticated
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

# --- REST ENDPOINTS ---
@app.get("/")
def root():
    return {"message": "API is running. GraphQL endpoint is at /graphql"}

@app.get("/api/admin", dependencies=[Depends(require_role(["Admin"]))])
def admin_rest_endpoint():
    """An example of a protected REST endpoint using the dependency factory."""
    return {"message": "Welcome, Admin. You have accessed a protected REST API endpoint."}

# --- SERVER START ---
if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)