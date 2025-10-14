# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["BrowserOpenResponse"]


class BrowserOpenResponse(BaseModel):
    cdp_url: str = FieldInfo(alias="cdpUrl")
    """The CDP url.

    You can use this URL with CDP libraries like puppeteer/playwright/etc.
    """
