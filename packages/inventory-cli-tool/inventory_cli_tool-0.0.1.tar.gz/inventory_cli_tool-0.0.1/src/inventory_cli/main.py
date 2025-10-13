from fastapi import FastAPI
from api.router import router as api_router

# Metadata for Swagger Docs
app = FastAPI(
    title="Inventory API",
    description="A simple but complete CRUD API built with FastAPI and MongoDB.",
    version="1.0.0",
    contact={
        "name": "API Support",
         "url": "https://www.example.com/contact",
        "email": "your.email@example.com",
    },
)

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Inventory API!"}

# Include the API router
app.include_router(api_router, prefix="/api/items", tags=["Items"])