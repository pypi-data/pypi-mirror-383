# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional, Union

from typing_extensions import Annotated, TypeAlias

from ....._models import BaseModel
from ....._utils import PropertyInfo
from .run_step_delta_message_delta import RunStepDeltaMessageDelta
from .tool_call_delta_object import ToolCallDeltaObject

__all__ = ["RunStepDelta", "StepDetails"]

StepDetails: TypeAlias = Annotated[
    Union[RunStepDeltaMessageDelta, ToolCallDeltaObject],
    PropertyInfo(discriminator="type"),
]


class RunStepDelta(BaseModel):
    step_details: Optional[StepDetails] = None
    """The details of the run step."""
