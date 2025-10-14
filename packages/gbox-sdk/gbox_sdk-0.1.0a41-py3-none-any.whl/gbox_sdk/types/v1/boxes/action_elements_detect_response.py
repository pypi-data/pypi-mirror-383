# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .detected_element import DetectedElement

__all__ = ["ActionElementsDetectResponse", "Screenshot", "ScreenshotMarked", "ScreenshotSource"]


class ScreenshotMarked(BaseModel):
    uri: str
    """URL of the screenshot"""

    presigned_url: Optional[str] = FieldInfo(alias="presignedUrl", default=None)
    """Presigned url of the screenshot"""


class ScreenshotSource(BaseModel):
    uri: str
    """URL of the screenshot"""

    presigned_url: Optional[str] = FieldInfo(alias="presignedUrl", default=None)
    """Presigned url of the screenshot"""


class Screenshot(BaseModel):
    marked: ScreenshotMarked
    """Result of screenshot capture action"""

    source: ScreenshotSource
    """Result of screenshot capture action"""


class ActionElementsDetectResponse(BaseModel):
    elements: List[DetectedElement]
    """Detected UI elements"""

    screenshot: Screenshot
    """Detected elements screenshot"""
