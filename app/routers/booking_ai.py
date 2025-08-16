import logging
import re
from datetime import datetime, timedelta, timezone
from typing import List, Optional
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

# Pacific timezone (PST/PDT)
PACIFIC_TZ = timezone(timedelta(hours=-8))  # PST is UTC-8

router = APIRouter(
    prefix="/bumi/ai",
    tags=["bumi-booking-ai"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


def parse_natural_datetime(text: str) -> Optional[str]:
    """Parse natural language date/time into ISO format"""
    text = text.lower().strip()

    # Current time for reference - use Pacific time
    now = datetime.now(PACIFIC_TZ)

    # Parse "august 30 at 3" or "aug 30 at 3pm" or "30th at 3"
    month_patterns = [
        r"(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|october|oct|november|nov|december|dec)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
        r"(\d{1,2})(?:st|nd|rd|th)?\s+(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|october|oct|november|nov|december|dec)\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
    ]

    for pattern in month_patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()

            # Determine which groups contain what
            if len(groups) == 5:  # month day hour minute ampm
                month_str, day_str, hour_str, minute_str, ampm = groups
                month = month_str
                day = int(day_str)
                hour = int(hour_str)
                minute = int(minute_str) if minute_str else 0
            elif len(groups) == 4:  # month day hour ampm
                month_str, day_str, hour_str, ampm = groups
                month = month_str
                day = int(day_str)
                hour = int(hour_str)
                minute = 0
            else:
                continue

            # Convert month name to number
            month_map = {
                "january": 1,
                "jan": 1,
                "february": 2,
                "feb": 2,
                "march": 3,
                "mar": 3,
                "april": 4,
                "apr": 4,
                "may": 5,
                "june": 6,
                "jun": 6,
                "july": 7,
                "jul": 7,
                "august": 8,
                "aug": 8,
                "september": 9,
                "sep": 9,
                "october": 10,
                "oct": 10,
                "november": 11,
                "nov": 11,
                "december": 12,
                "dec": 12,
            }

            month_num = month_map.get(month.lower())
            if not month_num:
                continue

            # Handle AM/PM
            if ampm:
                if ampm == "pm" and hour != 12:
                    hour += 12
                elif ampm == "am" and hour == 12:
                    hour = 0

            # Set year (assume current year or next year if date has passed)
            year = now.year
            if month_num < now.month or (month_num == now.month and day < now.day):
                year += 1

            try:
                # Create timezone-aware datetime in Pacific time
                dt = datetime(year, month_num, day, hour, minute, tzinfo=PACIFIC_TZ)
                return dt.isoformat()
            except ValueError:
                continue

    # Parse "tomorrow at 3pm" or "next friday at 2"
    if "tomorrow" in text:
        tomorrow = now + timedelta(days=1)
        time_match = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            ampm = time_match.group(3)

            if ampm:
                if ampm == "pm" and hour != 12:
                    hour += 12
                elif ampm == "am" and hour == 12:
                    hour = 0

            dt = datetime(
                tomorrow.year,
                tomorrow.month,
                tomorrow.day,
                hour,
                minute,
                tzinfo=timezone.utc,
            )
            return dt.isoformat()

        # Parse "next week" or "next friday"
    if "next week" in text:
        next_week = now + timedelta(weeks=1)
        # Default to same day of week, same time
        dt = datetime(
            next_week.year, next_week.month, next_week.day, 9, 0, tzinfo=timezone.utc
        )  # Default to 9 AM
        return dt.isoformat()

    # Parse "next monday", "next tuesday", etc.
    weekday_map = {
        "monday": 0,
        "mon": 0,
        "tuesday": 1,
        "tue": 1,
        "wednesday": 2,
        "wed": 2,
        "thursday": 3,
        "thu": 3,
        "friday": 4,
        "fri": 4,
        "saturday": 5,
        "sat": 5,
        "sunday": 6,
        "sun": 6,
    }

    for weekday_name, weekday_num in weekday_map.items():
        if f"next {weekday_name}" in text:
            current_weekday = now.weekday()
            days_ahead = weekday_num - current_weekday
            if days_ahead <= 0:  # Target day has passed this week
                days_ahead += 7
            target_date = now + timedelta(days=days_ahead)

            # Extract time if specified
            time_match = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                ampm = time_match.group(3)

                if ampm:
                    if ampm == "pm" and hour != 12:
                        hour += 12
                    elif ampm == "am" and hour == 12:
                        hour = 0
            else:
                # Default to 9 AM if no time specified
                hour, minute = 9, 0

            dt = datetime(
                target_date.year,
                target_date.month,
                target_date.day,
                hour,
                minute,
                tzinfo=timezone.utc,
            )
            return dt.isoformat()

    return None


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
- Cancel bookings when users say "cancel X booking", "cancel move out cleaning", etc.
- Uncancel/reactivate bookings when users say "uncancel X booking", "reactivate X booking", etc.
- Reschedule bookings when users say "reschedule X booking to Y time", "move X appointment to Y", etc.
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
- message should be friendly, dog-like and confirm the action (without specific time)
- reason should briefly explain what action is being taken
- ALWAYS use a booking_id that exists in the user's bookings list
- NEVER ask for clarification - execute the action directly based on the command
- Match service names from the command to service titles in the user's bookings
- For reschedule: use the exact date/time from the user's command
- Handle relative dates like "next week", "next monday", "tomorrow" based on the current date provided

EXAMPLES:

Cancel request:
User: "Cancel move out cleaning"
Response: {
  "action": "execute_booking_action",
  "message": "🐕 Woof! Cancelling your move-out cleaning! Time to call it a ruff day!",
  "action_type": "cancel",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "new_time": null,
  "reason": "Cancelling move-out cleaning booking as requested"
}

Uncancel request:
User: "Uncancel deep kitchen cleaning"
Response: {
  "action": "execute_booking_action",
  "message": "🎾 Yay! Reactivating your deep kitchen cleaning! Back in the game, no more ruff times!",
  "action_type": "uncancel",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "new_time": null,
  "reason": "Reactivating cancelled deep kitchen cleaning booking"
}

Reschedule request:
User: "Reschedule deep kitchen cleaning to august 30 at 3"
Response: {
  "action": "execute_booking_action",
  "message": "🐾 Sure thing! Moving your deep kitchen cleaning to August 30! Time to fetch a new time slot!",
  "action_type": "reschedule",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "new_time": "2024-08-30T15:00:00Z",
  "reason": "Rescheduling deep kitchen cleaning to August 30 at 3 PM"
}

Relative date request:
User: "Reschedule kitchen cleaning to next monday at 2pm"
Response: {
  "action": "execute_booking_action",
  "message": "🐾 Sure thing! Moving your kitchen cleaning to next Monday! Time to fetch a new time slot!",
  "action_type": "reschedule",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000",
  "new_time": "2024-01-15T14:00:00Z",
  "reason": "Rescheduling kitchen cleaning to next Monday at 2 PM"
}

IMPORTANT:
- ONLY respond with the JSON format above
- NEVER include additional text or explanations outside the JSON
- NEVER ask for clarification - execute actions directly
- Always provide a friendly, dog-like message with emojis at the start
- Use ONLY booking IDs that exist in the user's bookings
- Match service names from the command to service titles in the user's bookings
- Keep messages short and cheerful like a happy dog!
- Include dog puns and "ruff" references when paw-sible! 🐕‍🦺
- Keep reschedule messages simple - confirm the action without showing specific time
- Examples
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
        # Get the current user (customer only for now)
        user_customer = get_user_scoped_record(session, Customer, supabase_user_id)

        if not user_customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Get customer's bookings
        bookings = get_all_by_field(session, Booking, "customer_id", user_customer.id)

        logger.info(
            "[LOG] Found %d bookings for user %s", len(bookings), supabase_user_id
        )

        # Log the actual bookings for debugging
        for i, booking in enumerate(bookings):
            service = (
                session.get(Service, booking.service_id) if booking.service_id else None
            )
            service_name = service.service_title if service else "Unknown Service"
            logger.info(
                "[LOG] Booking %d: ID=%s, Service=%s, Status=%s, Date=%s",
                i + 1,
                booking.id,
                service_name,
                booking.status,
                booking.start_time.strftime("%Y-%m-%d %H:%M")
                if booking.start_time
                else "No date",
            )

        # Format bookings for AI context
        bookings_context = format_bookings_for_ai(bookings, session)

        # Build the prompt for the LLM
        user_message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])

        # Create system message with the booking AI prompt and user's bookings
        current_date = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
        system_content = f"{BOOKING_AI_SYSTEM_PROMPT}\n\nCURRENT DATE: {current_date}\n\n{bookings_context}"

        logger.info("[LOG] Current Date: %s", current_date)
        logger.info(
            "[LOG] AI System Prompt: %s",
            system_content[:500] + "..."
            if len(system_content) > 500
            else system_content,
        )
        logger.info("[LOG] User Message: %s", user_message)

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

        # Log the parsed response for debugging
        try:
            if isinstance(ai_response, dict):
                logger.info("[LOG] AI response parsed successfully: %s", ai_response)
            else:
                logger.warning("[LOG] AI response is not a dict: %s", type(ai_response))
        except Exception as e:
            logger.error("[LOG] Error parsing AI response: %s", e)

        # Check if this is a booking action request
        if ai_response.get("action") == "execute_booking_action":
            # Execute the booking action
            action_result = await execute_booking_action(
                ai_response, session, supabase_user_id, user_customer
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

        # Verify customer owns this booking
        if user_customer and booking.customer_id != user_customer.id:
            return {
                "success": False,
                "message": "You can only modify your own bookings",
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

            # Parse the new time - handle both ISO format and Z suffix
            try:
                if new_time.endswith("Z"):
                    # Convert Z to +00:00 for proper timezone handling
                    new_datetime = datetime.fromisoformat(
                        new_time.replace("Z", "+00:00")
                    )
                else:
                    # Already in proper ISO format
                    new_datetime = datetime.fromisoformat(new_time)

                logger.info(
                    "[LOG] Parsed datetime: %s (timezone: %s)",
                    new_datetime,
                    new_datetime.tzinfo,
                )
            except ValueError:
                return {
                    "success": False,
                    "message": "Invalid datetime format",
                    "error": "Invalid datetime format",
                }

            # Update booking start time - only include the field we want to update
            update_data = {"start_time": new_datetime}
            updated_booking = update_one(session, Booking, booking_id, update_data)

            # Simple message without specific time to avoid timezone confusion
            return {
                "success": True,
                "message": "Woof! Your booking has been rescheduled! 🐾",
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
