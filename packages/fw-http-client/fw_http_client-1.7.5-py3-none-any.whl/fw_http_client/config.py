"""HTTP client configuration."""

import typing as t
from importlib.metadata import version

from pydantic import BaseModel
from requests import PreparedRequest

__all__ = ["AnyAuth", "HttpConfig"]

RETRY_METHODS = ["DELETE", "GET", "HEAD", "POST", "PUT", "OPTIONS"]
RETRY_STATUSES = [429, 502, 503, 504]

AnyAuth = t.Union[
    str,  # authorization header (custom - the others are built in to requests)
    t.Tuple[str, str],  # basic auth username/password tuple
    t.Callable[[PreparedRequest], PreparedRequest],  # callable modifying the request
]


class HttpConfig(BaseModel):
    """HTTP client configuration."""

    client_name: str = "fw-http-client"
    client_version: str = version("fw_http_client")
    client_info: t.Dict[str, str] = {}

    baseurl: t.Optional[str] = None
    cookies: t.Dict[str, str] = {}
    headers: t.Dict[str, str] = {}
    params: t.Dict[str, str] = {}
    cert: t.Optional[t.Union[str, t.Tuple[str, str]]] = None
    auth: t.Optional[AnyAuth] = None
    proxies: t.Dict[str, str] = {}
    verify: bool = True
    trust_env: bool = True
    connect_timeout: float = 10
    read_timeout: float = 30
    max_redirects: int = 30
    stream: bool = False
    response_hooks: t.List[t.Callable] = []
    retry_backoff_factor: float = 0.5
    retry_allowed_methods: t.List[str] = RETRY_METHODS
    retry_status_forcelist: t.List[int] = RETRY_STATUSES
    retry_total: int = 5
