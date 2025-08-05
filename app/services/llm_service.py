import logging
import os
from typing import List, Optional

import openai

from app.models import Service
from app.models.chat import ChatRequest

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM service with OpenAI client"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = openai.OpenAI(api_key=self.api_key)

    def call_llm(self, prompt: str) -> str:
        """
        Call LLM with prompt

        Args:
            prompt: Combined prompt with instructions and user message

        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise

    @staticmethod
    def format_services_for_llm(services: List[Service]) -> str:
        service_string_for_llm = ""

        if not services:
            raise ValueError("No services are available to format for LLM.")

        for service in services:
            for key, val in service.model_dump().items():
                service_string_for_llm += f"{key}: {val}\n"
            service_string_for_llm += "---\n"
        heading = "AVAILABLE SERVICES:"

        return f"{heading}\n{service_string_for_llm}"

    @staticmethod
    def build_conversation_context(chat_request: ChatRequest) -> str:
        context = []
        for message in chat_request.conversation_history:
            context.append(f'User: "{message.user}"\nBumi: "{message.bumi}"')

        history_context = "\n".join(context)
        current_context = f'User: "{chat_request.message}"'

        result_context = f"CONVERSATION HISTORY:\n{history_context}\n\nCURRENT REQUEST: {current_context}"

        return result_context
