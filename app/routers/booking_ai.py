import logging
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.models.booking import Booking, BookingStatusUpdate
from app.models.customer import Customer
from app.models.provider import Provider
from app.models.service import Service
from app.services.llm_service import LLMService
from app.utils.auth import get_current_user_id
from app.utils.crud_helpers import get_all_by_field, get_one, update_one
from app.utils.user_helpers import get_user_scoped_record

router = APIRouter(
    prefix="/bumi/ai",
    tags=["bumi-booking-ai"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


def format_bookings_for_ai(bookings: List[Booking], session: Session) -> str:
    """Format user's bookings in a way that's useful for the AI to understand"""
    if not bookings:
        return "USER HAS NO BOOKINGS"

    booking_info = []
    for i, booking in enumerate(bookings, 1):
        # Get service details
        service = (
            session.get(Service, booking.service_id) if booking.service_id else None
        )
        service_name = service.service_title if service else "Unknown Service"

        # Get provider details
        provider = (
            session.get(Provider, booking.provider_id) if booking.provider_id else None
        )
        provider_name = provider.company_name if provider else "Unknown Provider"

        # Format the booking info in a more AI-friendly way
        booking_str = f"""
BOOKING #{i}:
- ID: {booking.id}
- Service: {service_name}
- Provider: {provider_name}
- Date: {booking.start_time.strftime("%A, %B %d, %Y")}
- Time: {booking.start_time.strftime("%I:%M %p")}
- Status: {booking.status}
- Address ID: {booking.address_id}
"""
        booking_info.append(booking_str)

    return f"USER'S BOOKINGS (Total: {len(bookings)}):\n" + "\n".join(booking_info)


BOOKING_AI_SYSTEM_PROMPT = """🐕 You are Bumi, a friendly and helpful AI assistant for managing home service bookings. You're like a smart dog that understands what humans want and helps them with their appointments! Time to fetch some booking updates!

IMPORTANT: You will be provided with the user's current bookings. Use this information to identify which specific booking they want to modify.

CAPABILITIES:
- Cancel bookings when users say "cancel my booking", "cancel X booking", etc.
- Uncancel/reactivate bookings when users say "uncancel my booking", "reactivate my booking", etc.
- Reschedule bookings when users say "reschedule my booking", "move my appointment", "change time", etc.
- Understand natural language requests and convert them to specific actions

⚠️ CRITICAL: You MUST respond with ONLY valid JSON. No other text allowed. ⚠️

RESPONSE FORMAT:
{
  "action": "execute_booking_action",
  "message": "🐾 Woof! I'll help you with that!",
  "action_type": "cancel|uncancel|reschedule",
  "booking_id": "uuid-string",
  "new_time": "2024-01-15T14:00:00Z" | null,
  "reason": "Brief explanation of what I'm doing"
}

RULES:
- For cancel: set action_type to "cancel", new_time to null
- For uncancel: set action_type to "uncancel", new_time to null  
- For reschedule: set action_type to "reschedule", new_time to ISO datetime string
- booking_id must be a valid UUID string from the user's bookings
- message should be friendly, dog-like and confirm the action
- reason should briefly explain what action is being taken
- ALWAYS use a booking_id that exists in the user's bookings list

EXAMPLES:

Cancel request:
User: "Please cancel my booking for tomorrow"
Response: {
  "action": "execute_booking_action",
  "message": "🐕 Woof! Cancelling your booking for tomorrow! Time to call it a ruff day!",
  "action_type": "cancel",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "new_time": null,
  "reason": "Cancelling booking as requested by user"
}

Uncancel request:
User: "Can you reactivate my cancelled booking?"
Response: {
  "action": "execute_booking_action",
  "message": "🎾 Yay! Reactivating your booking! Back in the game, no more ruff times!",
  "action_type": "uncancel",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "new_time": null,
  "reason": "Reactivating cancelled booking as requested by user"
}

Reschedule request:
User: "Can you move my appointment to 3 PM tomorrow?"
Response: {
  "action": "execute_booking_action",
  "message": "🐾 Sure thing! Moving your appointment to 3 PM tomorrow! Time to fetch a new time slot!",
  "action_type": "reschedule",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "new_time": "2024-01-15T15:00:00Z",
  "reason": "Rescheduling appointment to 3 PM tomorrow as requested"
}

IMPORTANT: 
- ONLY respond with the JSON format above
- NEVER include additional text or explanations outside the JSON
- If you can't determine the action, ask for clarification
- Always provide a friendly, dog-like message with emojis at the start
- Use ONLY booking IDs that exist in the user's bookings
- Keep messages short and cheerful like a happy dog!
- Include dog puns and "ruff" references when paw-sible! 🐕‍🦺
"""


@router.post("/quickTricks")
async def chat_with_booking_ai(
    request: dict,
    session: Session = Depends(get_session),
    supabase_user_id: UUID = Depends(get_current_user_id),
    llm_service: LLMService = Depends(lambda: LLMService()),
):
    """AI chat endpoint for booking modifications"""
    logger.info(
        "[LOG] Incoming booking AI message from user %s: %s",
        supabase_user_id,
        request.get("message"),
    )

    try:
        # Get the current user (customer or provider)
        user_customer = get_user_scoped_record(session, Customer, supabase_user_id)
        user_provider = get_user_scoped_record(session, Provider, supabase_user_id)

        if not user_customer and not user_provider:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's bookings
        if user_customer:
            bookings = get_all_by_field(
                session, Booking, "customer_id", user_customer.id
            )
        else:
            bookings = get_all_by_field(
                session, Booking, "provider_id", user_provider.id
            )

        logger.info(
            "[LOG] Found %d bookings for user %s", len(bookings), supabase_user_id
        )

        # Format bookings for AI context
        bookings_context = format_bookings_for_ai(bookings, session)

        # Build the prompt for the LLM
        user_message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])

        # Create system message with the booking AI prompt and user's bookings
        system_content = f"{BOOKING_AI_SYSTEM_PROMPT}\n\n{bookings_context}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ]

        # Add conversation history if available
        for msg in conversation_history:
            if msg.get("user"):
                messages.append({"role": "user", "content": msg["user"]})
            if msg.get("bumi"):
                messages.append({"role": "assistant", "content": msg["bumi"]})

        # Call the LLM
        ai_response = llm_service.call_llm(messages)
        logger.info("[LOG] AI response: %s", ai_response)

        # Check if this is a booking action request
        if ai_response.get("action") == "execute_booking_action":
            # Execute the booking action
            action_result = await execute_booking_action(
                ai_response, session, supabase_user_id, user_customer, user_provider
            )
            return {
                "action": "booking_action_executed",
                "message": action_result["message"],
                "success": action_result["success"],
                "details": action_result,
            }
        else:
            # Return the AI response as-is
            return ai_response

    except Exception as e:
        logger.error("[LOG] Error in booking AI chat: %s", e)
        raise HTTPException(
            status_code=500, detail=f"Error processing booking AI request: {str(e)}"
        )


async def execute_booking_action(
    ai_response: dict,
    session: Session,
    user_id: UUID,
    user_customer: Customer = None,
    user_provider: Provider = None,
) -> dict:
    """Execute the booking action based on AI response"""
    action_type = ai_response.get("action_type")
    booking_id = ai_response.get("booking_id")
    new_time = ai_response.get("new_time")

    if not action_type or not booking_id:
        return {"success": False, "message": "Missing action type or booking ID"}

    try:
        # Get the booking
        booking = get_one(session, Booking, booking_id)
        if not booking:
            return {
                "success": False,
                "message": f"Booking {booking_id} not found",
                "error": "Booking not found",
            }

        # Verify user owns this booking
        if user_customer and booking.customer_id != user_customer.id:
            return {
                "success": False,
                "message": "You can only modify your own bookings",
                "error": "Unauthorized",
            }
        elif user_provider and booking.provider_id != user_provider.id:
            return {
                "success": False,
                "message": "You can only modify bookings you're providing services for",
                "error": "Unauthorized",
            }

        if action_type == "cancel":
            # Update booking status to cancelled
            status_update = BookingStatusUpdate(status="cancelled")
            updated_booking = update_one(
                session, Booking, booking_id, status_update.model_dump()
            )
            return {
                "success": True,
                "message": "Woof! Your booking is now cancelled! 🐕",
                "booking": updated_booking,
                "action": "cancelled",
            }

        elif action_type == "uncancel":
            # Update booking status back to confirmed
            status_update = BookingStatusUpdate(status="confirmed")
            updated_booking = update_one(
                session, Booking, booking_id, status_update.model_dump()
            )
            return {
                "success": True,
                "message": "Yay! Your booking is reactivated! 🎾",
                "booking": updated_booking,
                "action": "uncancelled",
            }

        elif action_type == "reschedule":
            if not new_time:
                return {
                    "success": False,
                    "message": "New time required for rescheduling",
                    "error": "Missing new time",
                }

            # Parse the new time
            try:
                new_datetime = datetime.fromisoformat(new_time.replace("Z", "+00:00"))
            except ValueError:
                return {
                    "success": False,
                    "message": "Invalid datetime format",
                    "error": "Invalid datetime format",
                }

            # Update booking start time - only include the field we want to update
            update_data = {"start_time": new_datetime}
            updated_booking = update_one(session, Booking, booking_id, update_data)

            return {
                "success": True,
                "message": f"Woof! Your booking is now set for {new_datetime.strftime('%B %d, %Y at %I:%M %p')}! 🐾",
                "booking": updated_booking,
                "action": "rescheduled",
            }
        else:
            return {
                "success": False,
                "message": f"Invalid action type: {action_type}",
                "error": "Invalid action type",
            }

    except Exception as e:
        logger.error(f"[LOG] Error executing booking action: {e}")
        return {
            "success": False,
            "message": f"Error executing booking action: {str(e)}",
            "error": str(e),
        }


@router.get("/my-bookings")
async def get_user_bookings(
    session: Session = Depends(get_session),
    supabase_user_id: UUID = Depends(get_current_user_id),
):
    """Debug endpoint to see user's bookings"""
    try:
        # Get the current user (customer or provider)
        user_customer = get_user_scoped_record(session, Customer, supabase_user_id)
        user_provider = get_user_scoped_record(session, Provider, supabase_user_id)

        if not user_customer and not user_provider:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's bookings
        if user_customer:
            bookings = get_all_by_field(
                session, Booking, "customer_id", user_customer.id
            )
        else:
            bookings = get_all_by_field(
                session, Booking, "provider_id", user_provider.id
            )

        # Format bookings for display
        formatted_bookings = []
        for booking in bookings:
            service = (
                session.get(Service, booking.service_id) if booking.service_id else None
            )
            provider = (
                session.get(Provider, booking.provider_id)
                if booking.provider_id
                else None
            )

            formatted_bookings.append(
                {
                    "id": str(booking.id),
                    "service": service.title if service else "Unknown Service",
                    "provider": provider.company_name
                    if provider
                    else "Unknown Provider",
                    "date": booking.start_time.strftime("%Y-%m-%d"),
                    "time": booking.start_time.strftime("%I:%M %p"),
                    "status": booking.status,
                    "address_id": str(booking.address_id)
                    if booking.address_id
                    else None,
                }
            )

        return {
            "user_id": str(supabase_user_id),
            "user_type": "customer" if user_customer else "provider",
            "bookings_count": len(formatted_bookings),
            "bookings": formatted_bookings,
        }

    except Exception as e:
        logger.error("[LOG] Error getting user bookings: %s", e)
        raise HTTPException(
            status_code=500, detail=f"Error getting user bookings: {str(e)}"
        )
