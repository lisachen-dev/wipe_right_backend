from typing import List, Optional

from pydantic import BaseModel, Field


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
