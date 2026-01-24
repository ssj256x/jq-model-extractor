import uvicorn
from fastapi import FastAPI

from app.routes import user_routes

app = FastAPI(
    version="1.0.0",
    description="Sample python FastAPI application for JQ",
    docs_url="/docs",
)

app.include_router(user_routes.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
