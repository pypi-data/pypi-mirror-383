from __future__ import annotations

from typing import Optional

from typing_extensions import Annotated, Generic, TypeAlias, TypeVar, Union

from ...._compat import GenericModel
from ...._utils import PropertyInfo
from ....types.responses import (ParsedResponse, ResponseAudioDeltaEvent,
                                 ResponseAudioDoneEvent,
                                 ResponseAudioTranscriptDeltaEvent,
                                 ResponseAudioTranscriptDoneEvent,
                                 ResponseCodeInterpreterCallCodeDeltaEvent,
                                 ResponseCodeInterpreterCallCodeDoneEvent,
                                 ResponseCodeInterpreterCallCompletedEvent,
                                 ResponseCodeInterpreterCallInProgressEvent,
                                 ResponseCodeInterpreterCallInterpretingEvent)
from ....types.responses import \
    ResponseCompletedEvent as RawResponseCompletedEvent
from ....types.responses import (ResponseContentPartAddedEvent,
                                 ResponseContentPartDoneEvent,
                                 ResponseCreatedEvent,
                                 ResponseCustomToolCallInputDeltaEvent,
                                 ResponseCustomToolCallInputDoneEvent,
                                 ResponseErrorEvent, ResponseFailedEvent,
                                 ResponseFileSearchCallCompletedEvent,
                                 ResponseFileSearchCallInProgressEvent,
                                 ResponseFileSearchCallSearchingEvent)
from ....types.responses import \
    ResponseFunctionCallArgumentsDeltaEvent as \
    RawResponseFunctionCallArgumentsDeltaEvent
from ....types.responses import (ResponseFunctionCallArgumentsDoneEvent,
                                 ResponseImageGenCallCompletedEvent,
                                 ResponseImageGenCallGeneratingEvent,
                                 ResponseImageGenCallInProgressEvent,
                                 ResponseImageGenCallPartialImageEvent,
                                 ResponseIncompleteEvent,
                                 ResponseInProgressEvent,
                                 ResponseMcpCallArgumentsDeltaEvent,
                                 ResponseMcpCallArgumentsDoneEvent,
                                 ResponseMcpCallCompletedEvent,
                                 ResponseMcpCallFailedEvent,
                                 ResponseMcpCallInProgressEvent,
                                 ResponseMcpListToolsCompletedEvent,
                                 ResponseMcpListToolsFailedEvent,
                                 ResponseMcpListToolsInProgressEvent,
                                 ResponseOutputItemAddedEvent,
                                 ResponseOutputItemDoneEvent,
                                 ResponseOutputTextAnnotationAddedEvent,
                                 ResponseQueuedEvent,
                                 ResponseReasoningSummaryPartAddedEvent,
                                 ResponseReasoningSummaryPartDoneEvent,
                                 ResponseReasoningSummaryTextDeltaEvent,
                                 ResponseReasoningSummaryTextDoneEvent,
                                 ResponseRefusalDeltaEvent,
                                 ResponseRefusalDoneEvent)
from ....types.responses import \
    ResponseTextDeltaEvent as RawResponseTextDeltaEvent
from ....types.responses import \
    ResponseTextDoneEvent as RawResponseTextDoneEvent
from ....types.responses import (ResponseWebSearchCallCompletedEvent,
                                 ResponseWebSearchCallInProgressEvent,
                                 ResponseWebSearchCallSearchingEvent)
from ....types.responses.response_reasoning_text_delta_event import \
    ResponseReasoningTextDeltaEvent
from ....types.responses.response_reasoning_text_done_event import \
    ResponseReasoningTextDoneEvent

TextFormatT = TypeVar(
    "TextFormatT",
    # if it isn't given then we don't do any parsing
    default=None,
)


class ResponseTextDeltaEvent(RawResponseTextDeltaEvent):
    snapshot: str


class ResponseTextDoneEvent(RawResponseTextDoneEvent, GenericModel, Generic[TextFormatT]):
    parsed: Optional[TextFormatT] = None


class ResponseFunctionCallArgumentsDeltaEvent(RawResponseFunctionCallArgumentsDeltaEvent):
    snapshot: str


class ResponseCompletedEvent(RawResponseCompletedEvent, GenericModel, Generic[TextFormatT]):
    response: ParsedResponse[TextFormatT]  # type: ignore[assignment]


ResponseStreamEvent: TypeAlias = Annotated[
    Union[
        # wrappers with snapshots added on
        ResponseTextDeltaEvent,
        ResponseTextDoneEvent[TextFormatT],
        ResponseFunctionCallArgumentsDeltaEvent,
        ResponseCompletedEvent[TextFormatT],
        # the same as the non-accumulated API
        ResponseAudioDeltaEvent,
        ResponseAudioDoneEvent,
        ResponseAudioTranscriptDeltaEvent,
        ResponseAudioTranscriptDoneEvent,
        ResponseCodeInterpreterCallCodeDeltaEvent,
        ResponseCodeInterpreterCallCodeDoneEvent,
        ResponseCodeInterpreterCallCompletedEvent,
        ResponseCodeInterpreterCallInProgressEvent,
        ResponseCodeInterpreterCallInterpretingEvent,
        ResponseContentPartAddedEvent,
        ResponseContentPartDoneEvent,
        ResponseCreatedEvent,
        ResponseErrorEvent,
        ResponseFileSearchCallCompletedEvent,
        ResponseFileSearchCallInProgressEvent,
        ResponseFileSearchCallSearchingEvent,
        ResponseFunctionCallArgumentsDoneEvent,
        ResponseInProgressEvent,
        ResponseFailedEvent,
        ResponseIncompleteEvent,
        ResponseOutputItemAddedEvent,
        ResponseOutputItemDoneEvent,
        ResponseRefusalDeltaEvent,
        ResponseRefusalDoneEvent,
        ResponseTextDoneEvent,
        ResponseWebSearchCallCompletedEvent,
        ResponseWebSearchCallInProgressEvent,
        ResponseWebSearchCallSearchingEvent,
        ResponseReasoningSummaryPartAddedEvent,
        ResponseReasoningSummaryPartDoneEvent,
        ResponseReasoningSummaryTextDeltaEvent,
        ResponseReasoningSummaryTextDoneEvent,
        ResponseImageGenCallCompletedEvent,
        ResponseImageGenCallInProgressEvent,
        ResponseImageGenCallGeneratingEvent,
        ResponseImageGenCallPartialImageEvent,
        ResponseMcpCallCompletedEvent,
        ResponseMcpCallArgumentsDeltaEvent,
        ResponseMcpCallArgumentsDoneEvent,
        ResponseMcpCallFailedEvent,
        ResponseMcpCallInProgressEvent,
        ResponseMcpListToolsCompletedEvent,
        ResponseMcpListToolsFailedEvent,
        ResponseMcpListToolsInProgressEvent,
        ResponseOutputTextAnnotationAddedEvent,
        ResponseQueuedEvent,
        ResponseReasoningTextDeltaEvent,
        ResponseReasoningTextDoneEvent,
        ResponseCustomToolCallInputDeltaEvent,
        ResponseCustomToolCallInputDoneEvent,
    ],
    PropertyInfo(discriminator="type"),
]
