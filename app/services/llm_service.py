import logging
from textwrap import dedent
from typing import List, Optional

import openai

from app.config import (
    OPENAI_API_KEY,
    OPENAI_SYSTEM_PROMPT_FOOTER,
    OPENAI_SYSTEM_PROMPT_HEADER,
)
from app.models import Service
from app.models.chat import ChatRequest

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM service with OpenAI client"""
        self.api_key = api_key or OPENAI_API_KEY
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
        """
        Formats a list of services into a structured string for use in the LLM Prompt

        Args:
            services (List[Service]): list of services to include

        Returns:
            str: a formatted string describing the services.

        Raises:
             ValueError: if the list is empty
        """
        if not services:
            raise ValueError("No services are available to format for LLM.")

        service_lines = []
        for service in services:
            service_text_block = "\n".join(
                f"{key}: {val}" for key, val in service.model_dump().items()
            )
            service_lines.append(f"{service_text_block}\n---")

        return "AVAILABLE SERVICES:\n" + "\n".join(service_lines)

    @staticmethod
    def build_conversation_context(chat_request: ChatRequest) -> str:
        """
        Generates conversation context to use for the LLM Prompt based on chat history

        Args:
            chat_request (ChatRequest): contains message history and the current user message to LLM

        Returns:
            str: a formatted string with the past message (omits if not available) and the current user message
        """
        context = []
        for message in chat_request.conversation_history:
            context.append(f'User: "{message.user}"\nBumi: "{message.bumi}"')

        history_context = "\n".join(context)
        current_context = f'User: "{chat_request.message}"'

        return (
            "CONVERSATION HISTORY:\n"
            + history_context
            + "\n\nCURRENT REQUEST: "
            + current_context
            if history_context
            else "CURRENT REQUEST: " + current_context
        )

    @staticmethod
    def build_prompt(services: List[Service], chat_request: ChatRequest) -> str:
        """
        Constructs the full prompt to send to the LLM (instructions, services, conversation history and the user's current request.

        Args:
            services (List[Service]): services to include in the prompt.
            chat_request (ChatRequest): contains convo history and current message

        Returns:
            str: The complete prompt for the LLM
        """
        prompt_header = OPENAI_SYSTEM_PROMPT_HEADER
        service_context = LLMService.format_services_for_llm(services)
        conversation_context = LLMService.build_conversation_context(chat_request)
        prompt_footer = OPENAI_SYSTEM_PROMPT_FOOTER
        return dedent(f"""{prompt_header}

        {service_context}

        {conversation_context}

        {prompt_footer}""")
