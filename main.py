import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware
from gql.schemas import schema # Assuming this is your Strawberry schema file
from typing import Optional, Any
from auth import verify_token, User # Assuming auth.py is in the same directory

# --- CONTEXT GETTER ---
# This function will now be used to get the context for GraphQL.
# It relies on the verify_token dependency being resolved by FastAPI first.
async def get_context(request: Request, user: User = Depends(verify_token)):
    # The 'user' object is now available here because Depends(verify_token) was successful.
    # If verify_token had failed, it would have raised a 401 HTTPException and this code would not run.
    return {
        "request": request,
        "user": user
    }

# --- FASTAPI APP SETUP ---
app = FastAPI(title="Azure GraphQL Platform Processor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GRAPHQL ROUTER SETUP (MODIFIED) ---
# We now use Strawberry's GraphQLRouter and pass our context getter to it.
# The 'dependencies' parameter ensures verify_token is run for every GraphQL request.
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    # **CRITICAL CHANGE**: This enforces authentication on the entire GraphQL endpoint.
    dependencies=[Depends(verify_token)] 
)
app.include_router(graphql_app, prefix="/graphql")


# --- OTHER ENDPOINTS ---
@app.get("/")
async def root():
    return {"message": "Welcome to Azure GraphQL Platform Processor", "graphql_endpoint": "/graphql"}

# This protected REST endpoint remains for testing if needed.
@app.get("/api/protected")
async def protected_route(user: User = Depends(verify_token)):
    return {
        "message": "You have access to the protected REST API!",
        "user": {"id": user.id, "name": user.name, "roles": user.roles, "scopes": user.scp}
    }

# --- MAIN EXECUTION ---
def main():
    print("Starting GraphQL server...")
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)

if __name__ == "__main__":
    main()