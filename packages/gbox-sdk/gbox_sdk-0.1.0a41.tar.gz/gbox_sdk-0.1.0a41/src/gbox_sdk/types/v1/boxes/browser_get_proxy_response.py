# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["BrowserGetProxyResponse"]


class BrowserGetProxyResponse(BaseModel):
    http_server: str = FieldInfo(alias="httpServer")
    """HTTP proxy server, format: http://<username>:<password>@<host>:<port>"""

    https_server: str = FieldInfo(alias="httpsServer")
    """HTTPS proxy server, format: https://<username>:<password>@<host>:<port>"""

    socks5_server: str = FieldInfo(alias="socks5Server")
    """SOCKS5 proxy server, format: socks5://<username>:<password>@<host>:<port>"""

    bypass_list: Optional[List[str]] = FieldInfo(alias="bypassList", default=None)
    """List of IP addresses and domains that should bypass the proxy.

    These addresses will be accessed directly without going through the proxy
    server. Default is ['127.0.0.1', 'localhost']
    """

    pac_url: Optional[str] = FieldInfo(alias="pacUrl", default=None)
    """PAC (Proxy Auto-Configuration) URL."""
