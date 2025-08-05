import logging

from fastapi import APIRouter, Depends
from requests.sessions import Session

from app.db.session import get_session
from app.models.chat import ChatRequest, ChatResponse
from app.services.db_service import get_all_services
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
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(lambda: LLMService()),
):
    # pull all service data
    all_services = get_all_services(session)

    # build full prompt with services and chat history
    prompt = LLMService.build_prompt(services=all_services, chat_request=request)

    # send the prompt to the LLM
    ai_response = llm_service.call_llm(prompt)

    return ChatResponse(
        action="recommend",
        ai_message=ai_response,
        services=[],  # parse?
        clarification_question=None,
    )
