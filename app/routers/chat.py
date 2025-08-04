import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.services.llm_service import LLMService

router = APIRouter(
    prefix="/bumi/booking",
    tags=["bumi-chat"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


class ConversationMessage(BaseModel):
    user: str
    bumi: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's current message")
    conversation_history: List[ConversationMessage] = Field(
        default=[], description="Previous conversation messages"
    )


class ServiceRecommendation(BaseModel):
    id: str
    name: str
    provider: str
    price: float
    rating: float
    description: str
    category: str
    duration: int


class ChatResponse(BaseModel):
    action: str = Field(..., description="Either 'recommend' or 'clarify'")
    ai_message: str = Field(..., description="Bumi's response message")
    services: Optional[List[ServiceRecommendation]] = Field(
        default=None, description="Recommended services (only if action is 'recommend')"
    )
    clarification_question: Optional[str] = Field(
        default=None, description="Clarification question (only if action is 'clarify')"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_bumi(
    request: ChatRequest,
    llm_service: LLMService = Depends(lambda: LLMService()),
):
    ai_response = llm_service.call_llm(request.message)
    return ChatResponse(
        action="recommend",
        ai_message=ai_response,
        services=[],
        clarification_question=None,
    )
