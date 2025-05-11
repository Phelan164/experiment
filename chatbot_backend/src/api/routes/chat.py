import json
from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from src.llm.chatbot import chat, create_agent
import logging

router = APIRouter(prefix="/api", tags=["chat"])

agent = create_agent()

logger = logging.getLogger(__name__)


@router.post("/chat")
async def chat_api(request: Request):
    try:
        # Get session ID from query params
        session_id = request.query_params.get("session_id") or "123" # session_id to chatbot continue with the same conversation

        # Get request body
        body = await request.json()
        message = body.get("message")

        async def generate():
            try:
                answer = await chat(
                    message, session_id, agent
                )
                
                yield json.dumps(
                    {
                        "message": answer,
                    }
                )
            except Exception as e:
                logger.exception("Error in generate function")
                yield json.dumps(
                    {
                        "error": str(e),
                        "message": "An error occurred while processing your request",
                    }
                )

        return StreamingResponse(
            generate(),
            media_type="application/json",
            headers={"Connection": "keep-alive"},
        )

    except Exception as e:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))
