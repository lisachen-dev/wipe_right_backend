from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    RECOMMEND = "recommend"
    CLARIFY = "clarify"


class ConversationMessage(BaseModel):
    user: str
    bumi: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's current message")
    conversation_history: List[ConversationMessage] = Field(
        default=[], description="Previous conversation messages"
    )
    image: Optional[str] = Field(
        default=None,
        description="Base64 encoded image data (optional, for vision functionality)",
    )


class ServiceRecommendation(BaseModel):
    id: str
    name: str
    provider: str
    provider_id: str
    price: float
    rating: float
    description: str
    category: str
    duration: int
    available_time: Optional[datetime] = None


class ChatResponse(BaseModel):
    action: ActionType = Field(..., description="Either 'recommend' or 'clarify'")
    ai_message: str = Field(..., description="Here are some services that may help.")
    services: Optional[List[ServiceRecommendation]] = Field(
        default=None, description="..."
    )
    clarification_question: Optional[str] = Field(
        default=None, description="Clarification question (only if action is 'clarify')"
    )
