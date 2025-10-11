# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union

from typing_extensions import Annotated, TypeAlias

from ...._utils import PropertyInfo
from .image_file_content_block import ImageFileContentBlock
from .image_url_content_block import ImageURLContentBlock
from .refusal_content_block import RefusalContentBlock
from .text_content_block import TextContentBlock

__all__ = ["MessageContent"]


MessageContent: TypeAlias = Annotated[
    Union[
        ImageFileContentBlock,
        ImageURLContentBlock,
        TextContentBlock,
        RefusalContentBlock,
    ],
    PropertyInfo(discriminator="type"),
]
