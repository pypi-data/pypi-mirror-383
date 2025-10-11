# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union

from typing_extensions import TypeAlias

from .code_interpreter_tool_param import CodeInterpreterToolParam
from .file_search_tool_param import FileSearchToolParam
from .function_tool_param import FunctionToolParam

__all__ = ["AssistantToolParam"]

AssistantToolParam: TypeAlias = Union[
    CodeInterpreterToolParam, FileSearchToolParam, FunctionToolParam
]
