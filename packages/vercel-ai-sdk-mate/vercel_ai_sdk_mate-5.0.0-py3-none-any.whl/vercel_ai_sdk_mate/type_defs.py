# -*- coding: utf-8 -*-

import typing as T

T_REQUEST_BODY_TRIGGER_TYPE = T.Literal["submit-message",]

T_MESSAGE_ROLE_TYPE = T.Literal[
    "system",
    "user",
    "assistant",
]

T_MESSAGE_PART_TYPE_TYPE = T.Literal["text",]

T_MESSAGE_PART_STATE_TYPE = T.Literal[
    "streaming",
    "done",
]

T_RECORD_TYPE = dict[str, T.Any]
