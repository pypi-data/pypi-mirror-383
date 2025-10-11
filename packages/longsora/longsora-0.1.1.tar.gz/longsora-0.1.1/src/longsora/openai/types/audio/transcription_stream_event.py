# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union

from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .transcription_text_delta_event import TranscriptionTextDeltaEvent
from .transcription_text_done_event import TranscriptionTextDoneEvent

__all__ = ["TranscriptionStreamEvent"]

TranscriptionStreamEvent: TypeAlias = Annotated[
    Union[TranscriptionTextDeltaEvent, TranscriptionTextDoneEvent],
    PropertyInfo(discriminator="type"),
]
