# -*- coding: utf-8 -*-

import typing as T
import enum


class RequestBodyTriggerEnum(str, enum.Enum):
    SUBMIT_MESSAGE = "submit-message"


class MessageRoleEnum(str, enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessagePartTypeEnum(str, enum.Enum):
    TEXT = "text"
    REASONING = "reasoning"


class MessagePartStateEnum(str, enum.Enum):
    STREAMING = "streaming"
    DONE = "done"
