# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union

from typing_extensions import Annotated, TypeAlias

from ....._utils import PropertyInfo
from .code_interpreter_tool_call import CodeInterpreterToolCall
from .file_search_tool_call import FileSearchToolCall
from .function_tool_call import FunctionToolCall

__all__ = ["ToolCall"]

ToolCall: TypeAlias = Annotated[
    Union[CodeInterpreterToolCall, FileSearchToolCall, FunctionToolCall],
    PropertyInfo(discriminator="type"),
]
