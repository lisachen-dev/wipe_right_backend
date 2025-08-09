import base64
import json
import logging
from typing import List, Optional

import openai
from fastapi import HTTPException
from openai import OpenAIError
from openai.types.chat import ChatCompletionUserMessageParam

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

    def call_llm(
        self, messages: List[ChatCompletionUserMessageParam]
    ) -> ChatCompletionUserMessageParam:
        """
        Call LLM with a single user provided prompt
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=messages,
                temperature=0.3,
                max_tokens=500,
            )
            raw_response = response.choices[0].message.content
            logger.debug(f"Raw LLM response: {raw_response}")
            return json.loads(raw_response)

        except json.JSONDecodeError as e:
            logger.error(f"Bumi response error: {e.msg}")
            raise HTTPException(status_code=500, detail=f"Bumi response error: {e.msg}")

        except OpenAIError:
            logger.exception("OpenAI API error occurred")
            raise HTTPException(status_code=500, detail="OpenAI API call failed.")

    @staticmethod
    def format_services_for_llm(services: List[Service]) -> str:
        """
        Converts services into a clean JSON string for LLM consumption.
        Only includes fields relevant for the recommendation.
        """
        if not services:
            raise ValueError("No services are available to format for LLM.")

        service_lines = []
        for service in services:
            service_info = {
                "id": str(service.id),
                "service_title": service.service_title,
                "service_description": service.service_description,
                "pricing": service.pricing,
                "duration": service.duration,
                "category": service.category,
                "services_subcategories": service.services_subcategories,
            }

            if service.provider:
                service_info["provider_company_name"] = service.provider.company_name
                service_info["provider_name"] = (
                    f"{service.provider.first_name} {service.provider.last_name}"
                )

            service_text_block = "\n".join(
                f"{key}: {val}" for key, val in service_info.items() if val is not None
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
    def build_prompt(
        services: List[Service], chat_request: ChatRequest
    ) -> List[ChatCompletionUserMessageParam]:
        """
        Builds the structured messages array for OpenAI's ChatCompletion API using proper roles.
        Includes: one 'system' message, conversation history, and the user's current message.
        Supports vision functionality with optional image content.
        """

        system_prompt = "\n\n".join(
            [
                OPENAI_SYSTEM_PROMPT_HEADER.strip(),
                LLMService.format_services_for_llm(services),
                OPENAI_SYSTEM_PROMPT_FOOTER.strip(),
            ]
        )

        messages: List[ChatCompletionUserMessageParam] = [
            {"role": "system", "content": system_prompt}
        ]

        # Add chat history using user and bumi roles
        for msg in chat_request.conversation_history:
            if msg.user:
                messages.append({"role": "user", "content": msg.user})
            if msg.bumi:
                messages.append({"role": "assistant", "content": msg.bumi})

        # Add current user message with optional image
        current_message_content = []

        # Add text message if provided
        if chat_request.message:
            current_message_content.append(
                {"type": "text", "text": chat_request.message}
            )

        # Add image if provided
        if chat_request.image:
            try:
                # Validate base64 image
                base64.b64decode(chat_request.image)
                current_message_content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{chat_request.image}"
                        },
                    }
                )
            except Exception as e:
                logger.warning(f"Invalid base64 image data: {e}")
                # Continue without image if invalid

        if current_message_content:
            messages.append({"role": "user", "content": current_message_content})

        return messages
