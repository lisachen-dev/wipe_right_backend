import base64
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session

from app.db.session import get_session
from app.models import Service
from app.models.chat import ActionType, ChatRequest, ChatResponse, ConversationMessage
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
    """Main chat endpoint for JSON requests"""
    logger.info("[LOG] Incoming message: %s", request.message)
    return await _process_chat_request(request, session, llm_service)


@router.post("/chat/image", response_model=ChatResponse)
async def chat_with_bumi_image(
    message: str = Form(..., description="The user's current message"),
    conversation_history: str = Form(
        default="[]", description="JSON string of conversation history"
    ),
    image: UploadFile = File(..., description="Image file for vision functionality"),
    session: Session = Depends(get_session),
    llm_service: LLMService = Depends(lambda: LLMService()),
):
    """Chat endpoint with image upload for vision functionality"""
    logger.info("[LOG] Incoming image message: %s", message)

    # Parse conversation history
    try:
        import json

        history_data = json.loads(conversation_history)
        conversation_messages = [ConversationMessage(**msg) for msg in history_data]
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Invalid conversation history format: {e}")
        conversation_messages = []

    # Handle image upload
    try:
        # Read and encode image
        image_data = await image.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        logger.info(
            f"[LOG] Image uploaded: {image.filename}, size: {len(image_data)} bytes"
        )
    except Exception as e:
        logger.error(f"[LOG] Error processing image: {e}")
        raise HTTPException(status_code=400, detail="Error processing uploaded image")

    # Create ChatRequest object
    request = ChatRequest(
        message=message, conversation_history=conversation_messages, image=image_base64
    )

    return await _process_chat_request(request, session, llm_service)


async def _process_chat_request(
    request: ChatRequest,
    session: Session,
    llm_service: LLMService,
) -> ChatResponse:
    """Shared logic for processing chat requests"""
    # pull all service data
    all_services = get_all_services(session)
    logger.info("[LOG] Retrieved %d services from DB", len(all_services))

    # build full prompt with services and chat history
    prompt = LLMService.build_prompt(services=all_services, chat_request=request)
    logger.debug("[LOG] Built prompt:\n%s", prompt)

    # send the prompt to the LLM
    try:
        ai_response = llm_service.call_llm(prompt)
        logger.info("[LLM RAW OUTPUT] %s", ai_response)
        logger.info("[LOG] Bumi action: %s", ai_response.get("action"))

    except ValueError:
        logger.exception("[LOG] LLM prompt building or input error.")
        raise HTTPException(status_code=400, detail="Bad request sent to LLM.")

    except Exception:
        logger.exception("[LOG] Unexpected error while calling LLM.")
        raise HTTPException(status_code=500, detail="Internal server error.")

    # parse selected services
    service_ids = ai_response.get("service_ids", [])
    logger.info("[LOG] Service IDs returned: %s", service_ids)

    action = ai_response.get("action", "recommend")
    if action == "recommend" and not service_ids:
        logger.warning("[LOG] action was 'recommend' but no services were returned")
        return ChatResponse(
            action=ActionType.CLARIFY,
            ai_message="Ruff! I couldn't find a matching service, but I’d love to help!",
            services=[],
            clarification_question="Can you tell me more about what kind of help you need?",
        )

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
        action=ActionType(ai_response.get("action", "recommend")),
        ai_message=ai_response.get("message", "No message provided"),
        services=recommended_services,
        clarification_question=ai_response.get("clarification_question"),
    )
