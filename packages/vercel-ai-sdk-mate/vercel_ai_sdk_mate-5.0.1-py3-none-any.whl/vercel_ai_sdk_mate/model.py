# -*- coding: utf-8 -*-

"""
Data model for Vercel AI SDK v5

Reference:

- https://ai-sdk.dev/docs/introduction
- https://ai-sdk.dev/docs/migration-guides/migration-guide-5-0
"""

import typing as T
from pydantic import BaseModel, Field

from .constants import (
    RequestBodyTriggerEnum,
    MessageRoleEnum,
    MessagePartTypeEnum,
)
from .type_defs import (
    T_REQUEST_BODY_TRIGGER_TYPE,
    T_MESSAGE_ROLE_TYPE,
    T_MESSAGE_PART_TYPE_TYPE,
    T_MESSAGE_PART_STATE_TYPE,
    T_RECORD_TYPE,
)


class BaseMessagePart(BaseModel):
    type: T_MESSAGE_PART_TYPE_TYPE = Field()


class TextUIPart(BaseMessagePart):
    """
    Ref:

    - https://ai-sdk.dev/docs/reference/ai-sdk-core/ui-message#textuipart
    """

    type: T.Literal["text"] = Field(default=MessagePartTypeEnum.TEXT.value)
    text: str = Field()
    state: T_MESSAGE_PART_STATE_TYPE | None = Field(default=None)


class ReasoningUIPart(BaseMessagePart):
    """
    Ref:

    - https://ai-sdk.dev/docs/reference/ai-sdk-core/ui-message#reasoninguipart
    """

    type: T.Literal["reasoning"] = Field(default=MessagePartTypeEnum.REASONING.value)
    text: str = Field()
    state: T_MESSAGE_PART_STATE_TYPE | None = Field(default=None)
    providerMetadata: T_RECORD_TYPE | None = Field(default=None)


T_PART = T.Union[
    TextUIPart,
    ReasoningUIPart,
]


class Message(BaseModel):
    """
    Ref:

    - https://ai-sdk.dev/docs/reference/ai-sdk-core/ui-message
    """

    id: str = Field()
    role: T_MESSAGE_ROLE_TYPE = Field()
    parts: list[T.Annotated[T_PART, Field(discriminator="type")]] = Field()


class RequestBody(BaseModel):
    """
    Ref:

    - https://ai-sdk.dev/docs/ai-sdk-ui/chatbot#advanced-trigger-based-routing
    """

    id: str = Field()
    messages: list[Message] = Field()
    trigger: T_REQUEST_BODY_TRIGGER_TYPE = Field()
