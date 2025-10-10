"""HTTP API Protocol types matching the SPEC.md definition.

These types define the external contract for the Zowie Agent SDK API.
They handle automatic camelCase serialization for JSON communication.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )


# Request types


class Metadata(CamelCaseModel):
    """Request metadata from the external API."""

    requestId: str
    chatbotId: str
    conversationId: str
    interactionId: Optional[str] = None


class Message(CamelCaseModel):
    """Chat message in the conversation."""

    author: Literal["User", "Chatbot"]
    content: str
    timestamp: datetime


class Persona(CamelCaseModel):
    """Agent persona configuration.

    Uses snake_case internally but serializes to/from camelCase for the API.
    """

    name: Optional[str] = None
    business_context: Optional[str] = None
    tone_of_voice: Optional[str] = None


# Response command types


class SendMessagePayload(CamelCaseModel):
    """Payload for send_message command."""

    message: str


class SendMessageCommand(CamelCaseModel):
    """Command to send a message to the user."""

    type: Literal["send_message"] = "send_message"
    payload: SendMessagePayload


class GoToNextBlockPayload(CamelCaseModel):
    """Payload for go_to_next_block command."""

    message: Optional[str] = None
    nextBlockReferenceKey: str


class GoToNextBlockCommand(CamelCaseModel):
    """Command to transfer control to another block."""

    type: Literal["go_to_next_block"] = "go_to_next_block"
    payload: GoToNextBlockPayload


Command = Annotated[
    Union[SendMessageCommand, GoToNextBlockCommand],
    Field(discriminator="type"),
]


# Event types


class LLMCallEventPayload(CamelCaseModel):
    """Payload for LLM call events."""

    prompt: str
    response: str
    model: str
    durationInMillis: int


class LLMCallEvent(CamelCaseModel):
    """Event tracking an LLM API call."""

    type: Literal["llm_call"] = "llm_call"
    payload: LLMCallEventPayload


class APICallEventPayload(CamelCaseModel):
    """Payload for API call events."""

    url: str
    requestHeaders: Dict[str, str]
    requestMethod: str
    requestBody: Optional[str]
    responseHeaders: Dict[str, str]
    responseStatusCode: int
    responseBody: Optional[str]
    durationInMillis: int


class APICallEvent(CamelCaseModel):
    """Event tracking an external API call."""

    type: Literal["api_call"] = "api_call"
    payload: APICallEventPayload


Event = Annotated[Union[LLMCallEvent, APICallEvent], Field(discriminator="type")]


# Incoming request validation
class IncomingRequest(CamelCaseModel):
    """Complete request validation model matching SPEC.md."""

    metadata: Metadata
    messages: List[Message]
    context: Optional[str] = None
    persona: Optional[Persona] = None


# Main response type
class ExternalAgentResponse(CamelCaseModel):
    """Response sent back to the external API."""

    command: Command
    valuesToSave: Optional[Dict[str, Any]] = None
    events: Optional[List[Event]] = None
