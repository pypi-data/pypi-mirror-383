# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union

from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .code_interpreter_tool import CodeInterpreterTool
from .file_search_tool import FileSearchTool
from .function_tool import FunctionTool

__all__ = ["AssistantTool"]

AssistantTool: TypeAlias = Annotated[
    Union[CodeInterpreterTool, FileSearchTool, FunctionTool],
    PropertyInfo(discriminator="type"),
]
