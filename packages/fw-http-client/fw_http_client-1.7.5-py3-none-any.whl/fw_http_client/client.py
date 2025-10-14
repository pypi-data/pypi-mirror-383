"""HTTP client."""

import dataclasses
import email.parser
import json
import typing as t
import warnings
from http import HTTPStatus

import requests
from fw_utils import AttrDict, attrify
from requests import exceptions
from requests.adapters import HTTPAdapter
from requests.cookies import cookiejar_from_dict
from requests.sessions import Session
from requests.structures import CaseInsensitiveDict
from urllib3.util.retry import Retry

from .config import HttpConfig
from .errors import ClientError, Conflict, NotFound, ServerError

__all__ = ["HttpClient", "load_useragent"]

KILOBYTE = 1 << 10
MEGABYTE = 1 << 20


class HttpClient(Session):
    """Prod-ready HTTP client with timeout and retries by default."""

    # TODO better separate original and added attrs in init
    # TODO implement / test retry adapter pickling
    # consider opt-in envvar parsing for config
    __attrs__ = Session.__attrs__ + ["config", "baseurl", "timeout"]

    def __init__(self, config: t.Optional[HttpConfig] = None, **kwargs) -> None:
        """Init client instance using attrs from HttpConfig."""
        super().__init__()
        self.config = config = config or HttpConfig(**kwargs)
        self.baseurl = config.baseurl or ""
        self.cookies = cookiejar_from_dict(config.cookies)
        user_agent = dump_useragent(
            config.client_name,
            config.client_version,
            **config.client_info,
        )
        config.headers.setdefault("User-Agent", user_agent)
        self.headers.update(config.headers)
        self.params.update(config.params)  # type: ignore
        self.cert = config.cert
        if isinstance(config.auth, str):
            self.headers["Authorization"] = config.auth
        else:
            self.auth = config.auth
        self.proxies = config.proxies
        self.verify = config.verify
        self.trust_env = config.trust_env
        self.timeout = (config.connect_timeout, config.read_timeout)
        self.max_redirects = config.max_redirects
        self.stream = config.stream
        self.hooks = {"response": config.response_hooks}
        retry = Retry(
            backoff_factor=config.retry_backoff_factor,
            allowed_methods=config.retry_allowed_methods,
            status_forcelist=config.retry_status_forcelist,
            raise_on_redirect=False,
            raise_on_status=False,
            total=config.retry_total,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

    def request(  # type: ignore
        self, method: str, url: str, raw: bool = False, **kwargs
    ):
        """Send request and return loaded JSON response (AttrDict)."""
        # prefix relative paths with baseurl
        if not url.startswith("http"):
            url = f"{self.baseurl}{url}"
        # set authorization header from simple str auth kwarg
        if isinstance(kwargs.get("auth"), str):
            headers = kwargs.setdefault("headers", {})
            headers["Authorization"] = kwargs.pop("auth")
        # use the session timeout by default
        kwargs.setdefault("timeout", self.timeout)
        response = super().request(method, url, **kwargs)
        response.__class__ = Response  # cast as subclass
        # raise if there was an http error (eg. 404)
        if not raw:
            response.raise_for_status()
        # return response when streaming or raw=True
        if raw or self.stream or kwargs.get("stream"):
            return response
        # don't load empty response as json
        if not response.content:
            return None
        return response.json()


def dump_useragent(name: str, version: str, **kwargs: str) -> str:
    """Return parsable UA string for given name, version and extra keywords."""
    info = "; ".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    info_str = f" ({info})" if kwargs else ""
    return f"{name}/{version}{info_str}"


def load_useragent(useragent: str) -> t.Dict[str, str]:
    """Return name, version and extra keywords parsed from UA string."""
    name, _, useragent = useragent.partition("/")
    version, _, useragent = useragent.partition(" ")
    info = {}
    info_str = useragent.strip("()")
    if info_str:
        for item in info_str.split("; "):
            key, value = item.split(":", maxsplit=1)
            info[key] = value
    return AttrDict(name=name, version=version, **info)


class Response(requests.Response):
    """Response with multipart and event-stream support plus attrified JSONs.

    iter_jsonl() - Parse and yield from JSONL responses. Refs:
      https://jsonlines.org/

    iter_parts() - Parse, split and yield multipart messages. Refs:
      https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
      https://github.com/requests/toolbelt/blob/0.9.1/requests_toolbelt/multipart/decoder.py#L74
      https://github.com/herrmannlab/dicomweb-client/blob/v0.57.1/src/dicomweb_client/web.py#L717

    iter_events() - Parse, split and yield server-sent events. Refs:
      https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events
      https://github.com/mpetazzoni/sseclient/tree/sseclient-py-1.7.2
      https://github.com/btubbs/sseclient/blob/v0.0.27/sseclient.py

    Changes:
      iter_contents()    - Default read chunk size is 1 MegaByte
      iter_lines()       - Default read chunk size is 1 KiloByte
      json()             - Return data attrified (dict keys are attr-accessible)
      raise_for_status() - Raise distinct HTTP errors for 4xx / 5xx statuses
    """

    def iter_jsonl(self, chunk_size: int = KILOBYTE) -> t.Iterator[t.Any]:
        """Yield individual JSON objects from each line of the response stream."""
        with self:
            for line in self.iter_lines(chunk_size=chunk_size):
                yield json.loads(line)

    def iter_parts(self, chunk_size: int = MEGABYTE) -> t.Iterator["Part"]:
        """Yield individual message parts from a multipart response stream."""
        content_type = self.headers["content-type"]
        ctype, *ct_info = [ct.strip() for ct in content_type.split(";")]
        if not ctype.lower().startswith("multipart"):
            raise ValueError(f"Content-Type is not multipart: {ctype}")
        for item in ct_info:
            attr, _, value = item.partition("=")
            if attr.lower() == "boundary":
                boundary = value.strip('"')
                break
        else:
            # Some servers set the media type to multipart but don't provide a
            # boundary and just send a single frame in the body - yield as is.
            yield Part(self.content, split_header=False)
            return
        message = b""
        delimiter = f"\r\n--{boundary}".encode()
        preamble = True
        with self:
            for chunk in self.iter_content(chunk_size=chunk_size):
                message += chunk
                if preamble and delimiter[2:] in message:
                    _, message = message.split(delimiter[2:], maxsplit=1)
                    preamble = False
                while delimiter in message:
                    content, message = message.split(delimiter, maxsplit=1)
                    yield Part(content)
        if not message.startswith(b"--"):
            warnings.warn("Last boundary is not a closing delimiter")

    def iter_events(self, chunk_size: int = KILOBYTE) -> t.Iterator["Event"]:
        """Yield individual events from a Server-Sent Event response stream."""
        content_type = self.headers["content-type"]
        ctype = content_type.split(";")[0].strip()
        if ctype.lower() != "text/event-stream":
            raise ValueError(f"Content-Type is not text/event-stream: {ctype}")

        def iter_sse_lines():
            """Yield lines from the response delimited by either CRLF, LF or CR."""
            buffer = ""
            eols = "\r\n", "\n", "\r"
            for chunk in self.iter_content(chunk_size=chunk_size, decode_unicode=True):
                buffer += chunk.decode() if isinstance(chunk, bytes) else chunk
                while eol := next((eol for eol in eols if eol in buffer), None):
                    # found a CR as the last char - read more in case it's a CRLF
                    if eol == "\r" and buffer.index(eol) == len(buffer) - 1:
                        break
                    line, buffer = buffer.split(eol, maxsplit=1)
                    yield line
            if buffer:
                yield buffer.rstrip("\r")

        with self:
            # TODO retry from last_id if connection lost
            event = Event()
            retry = last_id = None
            for line in iter_sse_lines():
                if line:
                    event.parse_line(line)
                    retry = event.retry or retry
                elif event.data:
                    if event.data.endswith("\n"):
                        event.data = event.data[:-1]
                    yield event
                    last_id = event.id or last_id
                    event = Event()

    def iter_content(self, chunk_size=MEGABYTE, decode_unicode=False):  # noqa: D102
        return super().iter_content(
            chunk_size=chunk_size,
            decode_unicode=decode_unicode,
        )

    def iter_lines(  # noqa: D102
        self, chunk_size=KILOBYTE, decode_unicode=False, delimiter=None
    ):
        return super().iter_lines(
            chunk_size=chunk_size,
            decode_unicode=decode_unicode,
            delimiter=delimiter,
        )

    def json(self, **kwargs):
        """Return loaded JSON response with attribute access enabled."""
        try:
            return attrify(super().json(**kwargs))
        except ValueError as exc:
            raise exceptions.InvalidJSONError(exc, response=self)

    def raise_for_status(self) -> None:
        """Raise ClientError for 4xx / ServerError for 5xx responses."""
        try:
            super().raise_for_status()
        except exceptions.HTTPError as exc:
            if self.status_code == HTTPStatus.NOT_FOUND:
                exc.__class__ = NotFound  # pragma: no cover
            elif self.status_code == HTTPStatus.CONFLICT:
                exc.__class__ = Conflict  # pragma: no cover
            elif self.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
                exc.__class__ = ClientError
            else:
                exc.__class__ = ServerError
            raise


@dataclasses.dataclass
class Part:
    """Single part of a multipart message with it's own headers and content."""

    headers: CaseInsensitiveDict
    content: bytes

    def __init__(self, content: bytes, split_header: bool = True):
        """Return message part with it's own headers and content."""
        if not split_header:
            headers = None
        elif b"\r\n\r\n" not in content:
            raise ValueError("Message part does not contain CRLF CRLF")
        else:
            header, content = content.split(b"\r\n\r\n", maxsplit=1)
            headers = email.parser.HeaderParser().parsestr(header.decode()).items()
        self.headers = CaseInsensitiveDict(headers or {})
        self.content = content


@dataclasses.dataclass
class Event:
    """Single event from a Server-Sent Event stream."""

    id: t.Optional[str] = None
    type: str = "message"
    data: str = ""
    retry: t.Optional[int] = None

    def parse_line(self, line: str) -> None:
        """Parse non-empty SSE line and incrementally update event attributes."""
        if line.startswith(":"):
            return
        if ":" not in line:
            line += ":"
        field, value = line.split(":", maxsplit=1)
        value = value[1:] if value.startswith(" ") else value
        if field == "id" and "\0" not in value:
            self.id = value
        elif field == "event":
            self.type = value
        elif field == "data":
            self.data += f"{value}\n"
        elif field == "retry" and value.isdigit():
            self.retry = int(value)
        return
