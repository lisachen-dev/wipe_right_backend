import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAIError
from sqlmodel import Session

from app.db.session import get_session
from app.models import Service
from app.models.chat import ChatRequest, ChatResponse
from app.services.db_access import get_all_services
from app.services.llm_service import LLMService
from app.services.transformers import map_services_to_recommendations
from app.utils.crud_helpers import get_all_by_ids_with_options

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
    logger.info("[LOG] Incoming message: %s", request.message)

    # pull all service data
    all_services = get_all_services(session)
    logger.info("[LOG] Retrieved %d services from DB", len(all_services))

    # build full prompt with services and chat history
    prompt = LLMService.build_prompt(services=all_services, chat_request=request)
    logger.debug("[LOG] Built prompt:\n%s", prompt)

    # send the prompt to the LLM
    try:
        ai_response = llm_service.call_llm(prompt)

    except OpenAIError as e:
        logger.exception("[LOG] LLM call failed due to OpenAI API issue.")
        raise HTTPException(status_code=500, detail="OpenAI API call failed.")

    except ValueError as e:
        logger.exception("[LOG] LLM prompt building or input error.")
        raise HTTPException(status_code=400, detail="Bad request sent to LLM.")

    except Exception as e:
        logger.exception("[LOG] Unexpected error while calling LLM.")
        raise HTTPException(status_code=500, detail="Internal server error.")

    # convert json to python object
    try:
        parsed_ai_response = json.loads(ai_response)
        logger.debug("[LOG] Parsed LLM response: %s", parsed_ai_response)

    except Exception as e:
        logger.exception("[LOG] Unexpected error parsing LLM response")
        raise HTTPException(status_code=500, detail=f"AI response error: {str(e)}")

    # parse selected services
    service_ids = parsed_ai_response.get("service_ids", [])
    logger.info("[LOG] Service IDs returned: %s", service_ids)

    services = get_all_by_ids_with_options(
        session=session,
        model=Service,
        ids=service_ids,
        relationship_attr=Service.provider,
    )

    logger.info("Loaded %d services from IDs", len(services))

    recommended_services = map_services_to_recommendations(services, session)
    logger.info("[LOG] Mapped recommended services: %s", recommended_services)

    return ChatResponse(
        action=parsed_ai_response.get("action", "recommend"),
        ai_message=parsed_ai_response.get("message", "No message provided"),
        services=recommended_services,
        clarification_question=parsed_ai_response.get("clarification_question"),
    )
