# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["MediaAlbum"]


class MediaAlbum(BaseModel):
    last_modified: datetime = FieldInfo(alias="lastModified")
    """Last modified time of the album"""

    media_count: float = FieldInfo(alias="mediaCount")
    """Number of media files in the album"""

    name: str
    """Name of the album"""

    path: str
    """Full path to the album in the box"""
