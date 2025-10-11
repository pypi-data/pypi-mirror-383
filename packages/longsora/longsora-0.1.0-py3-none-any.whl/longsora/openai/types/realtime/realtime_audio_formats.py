# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional, Union

from typing_extensions import Annotated, Literal, TypeAlias

from ..._models import BaseModel
from ..._utils import PropertyInfo

__all__ = ["RealtimeAudioFormats", "AudioPCM", "AudioPCMU", "AudioPCMA"]


class AudioPCM(BaseModel):
    rate: Optional[Literal[24000]] = None
    """The sample rate of the audio. Always `24000`."""

    type: Optional[Literal["audio/pcm"]] = None
    """The audio format. Always `audio/pcm`."""


class AudioPCMU(BaseModel):
    type: Optional[Literal["audio/pcmu"]] = None
    """The audio format. Always `audio/pcmu`."""


class AudioPCMA(BaseModel):
    type: Optional[Literal["audio/pcma"]] = None
    """The audio format. Always `audio/pcma`."""


RealtimeAudioFormats: TypeAlias = Annotated[
    Union[AudioPCM, AudioPCMU, AudioPCMA], PropertyInfo(discriminator="type")
]
