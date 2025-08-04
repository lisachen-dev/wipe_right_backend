import logging

from fastapi import APIRouter, Depends

from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService

router = APIRouter(
    prefix="/bumi/booking",
    tags=["bumi-chat"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


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
