# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union

from typing_extensions import TypeAlias

from .image_file_content_block_param import ImageFileContentBlockParam
from .image_url_content_block_param import ImageURLContentBlockParam
from .text_content_block_param import TextContentBlockParam

__all__ = ["MessageContentPartParam"]

MessageContentPartParam: TypeAlias = Union[
    ImageFileContentBlockParam, ImageURLContentBlockParam, TextContentBlockParam
]
