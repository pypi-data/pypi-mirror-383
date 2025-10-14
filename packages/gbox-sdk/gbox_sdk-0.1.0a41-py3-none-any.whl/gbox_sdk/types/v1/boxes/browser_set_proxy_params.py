# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo

__all__ = ["BrowserSetProxyParams"]


class BrowserSetProxyParams(TypedDict, total=False):
    http_server: Required[Annotated[str, PropertyInfo(alias="httpServer")]]
    """HTTP proxy server, format: http://<username>:<password>@<host>:<port>"""

    https_server: Required[Annotated[str, PropertyInfo(alias="httpsServer")]]
    """HTTPS proxy server, format: https://<username>:<password>@<host>:<port>"""

    socks5_server: Required[Annotated[str, PropertyInfo(alias="socks5Server")]]
    """SOCKS5 proxy server, format: socks5://<username>:<password>@<host>:<port>"""

    bypass_list: Annotated[SequenceNotStr[str], PropertyInfo(alias="bypassList")]
    """List of IP addresses and domains that should bypass the proxy.

    These addresses will be accessed directly without going through the proxy
    server. Default is ['127.0.0.1', 'localhost']
    """

    pac_url: Annotated[str, PropertyInfo(alias="pacUrl")]
    """PAC (Proxy Auto-Configuration) URL."""
