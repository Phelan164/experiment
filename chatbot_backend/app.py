from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.main import api_router
from src.config import s
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Chatbot API", description="API for the chatbot")

# Update CORS middleware with specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

logger.info(f"Starting app with host: {s.host}")

# Include the routers
app.include_router(api_router, prefix="")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)