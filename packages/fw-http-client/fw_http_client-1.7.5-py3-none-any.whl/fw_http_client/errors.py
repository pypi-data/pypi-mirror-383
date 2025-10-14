"""HTTP client errors."""

import io
import json
import re
import typing as t

# proxy all requests exceptions when accessed through the module
from requests.exceptions import *  # noqa: F403

# explicitly import the classes that are used directly
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    InvalidJSONError,
    RequestException,
    Timeout,
)

# define a limited set of explicitly exported errors
__all__ = [
    "ClientError",
    "Conflict",
    "ConnectionError",
    "HTTPError",
    "NotFound",
    "ServerError",
    "RequestException",
    "Timeout",
]

connection_error_str_orig = ConnectionError.__str__
http_error_str_orig = HTTPError.__str__
json_error_str_orig = InvalidJSONError.__str__
request_exception_str_orig = RequestException.__str__


class ClientError(HTTPError):
    """The server returned a response with a 4xx status code."""


class NotFound(ClientError):
    """The server returned a response with a 404 status code."""


class Conflict(ClientError):
    """The server returned a response with a 409 status code."""


class ServerError(HTTPError):
    """The server returned a response with a 5xx status code."""


def request_exception_getattr(self, name: str):
    """Proxy the response and the request attributes for convenience."""
    # TODO try to subclass requests exceptions in order to enable type-hinting
    # eg. add py.typed after refact so that downstream users can mypy .status_code
    try:
        return getattr(self.response, name)
    except AttributeError:
        pass
    try:
        return getattr(self.request, name)
    except AttributeError:
        pass
    raise AttributeError(f"{type(self).__name__} has no attribute {name!r}")


def request_exception_str(self) -> str:  # pragma: no cover
    """Return the string representation of a RequestException."""
    request = self.request or getattr(self.response, "request", None)

    # Fallback to the original string representation if we can't source a request object
    if not request:
        return request_exception_str_orig(self)

    return f"{request.method} {request.url} - {self.args[0]}"


def connection_error_str(self) -> str:
    """Return the string representation of a ConnectionError."""
    request = self.request or getattr(self.response, "request", None)

    # Fallback to the original string representation if we can't source a request object
    if not request:
        return connection_error_str_orig(self)

    msg = str(self.args[0])
    if "Errno" in msg:
        msg = re.sub(r".*(\[[^']*).*", r"\1", msg)
    if "read timeout" in msg:
        msg = re.sub(r'.*: ([^"]*).*', r"\1", msg)
    if "Connection aborted" in msg:  # TODO investigate: raised locally, not in ci
        msg = re.sub(r".*'([^']*)'.*", r"\1", msg)  # pragma: no cover
    return f"{request.method} {request.url} - {msg}"


def http_error_str(self) -> str:
    """Return the string representation of an HTTPError."""
    request = self.request or getattr(self.response, "request", None)

    # Fallback to the original string representation if we can't source a request object
    if not request:
        return http_error_str_orig(self)

    msg = (
        f"{request.method} {self.response.url} - "
        f"{self.response.status_code} {self.response.reason}"
    )
    if self.response.history:
        redirects = "\n".join(
            f"{request.method} {redirect.url} - "
            f"{redirect.status_code} {redirect.reason}"
            for redirect in self.response.history
        )
        msg = f"{redirects}\n{msg}"
    if error_message := get_error_message(stringify(self.response.content)):
        msg += f"\nResponse: {error_message}"
    return msg


def json_error_str(self) -> str:
    """Return the string representation of an InvalidJSONError."""
    request = self.request or getattr(self.response, "request", None)

    # Fallback to the original string representation if we can't source a request object
    if not request:
        return json_error_str_orig(self)

    msg = f"{request.method} {self.response.url} - invalid JSON"
    if self.response.content:
        msg += f" response: {truncate(stringify(self.response.content))}"
    return msg


def truncate(
    string: str, max_length_binary: int = 100, max_length_text: int = 1000
) -> str:
    """Return string truncated to be at most 'max_length' characters."""
    if string.startswith("b'") and len(string) > max_length_binary:
        string = string[: max_length_binary - 3].rstrip() + "..."
    elif len(string) > max_length_text:
        string = string[: max_length_text - 3].rstrip() + "..."
    return string.rstrip()


def get_error_message(message: str) -> str:
    """Return human-readable error message from a (possibly JSON) response."""
    try:
        if json_message := json.loads(message).get("message"):
            return json_message
    except Exception:
        pass
    return truncate(message)


def stringify(data: t.Union[t.IO, bytes, str, None]) -> str:
    """Return string representation of a request- or response body."""
    if not data:
        return ""
    # requests.post(url, data=open(file))
    name = getattr(data, "name", None)
    if name:  # pragma: no cover
        return f"file://{name}"
    # requests.post(url, data=BytesIO(b"foo"))
    if isinstance(data, io.BytesIO):  # pragma: no cover
        data = data.getvalue()
    try:
        return data.decode()  # type: ignore
    except (AttributeError, UnicodeDecodeError):  # pragma: no cover
        return str(data)
