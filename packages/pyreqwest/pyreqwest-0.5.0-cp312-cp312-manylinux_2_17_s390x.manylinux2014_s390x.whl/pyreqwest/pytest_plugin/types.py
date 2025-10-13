"""Types used in the pytest plugin."""

from collections.abc import Awaitable, Callable
from re import Pattern
from typing import Any

from pyreqwest.http import Url
from pyreqwest.request import Request
from pyreqwest.response import Response, SyncResponse

try:
    from dirty_equals import DirtyEquals

    Matcher = str | Pattern[str] | DirtyEquals[Any]
    JsonMatcher = DirtyEquals[Any] | Any
except ImportError:
    Matcher = str | Pattern[str]  # type: ignore[misc]
    JsonMatcher = Any  # type: ignore[assignment,misc]

MethodMatcher = Matcher
PathMatcher = Matcher
UrlMatcher = Matcher | Url
QueryMatcher = dict[str, Matcher | list[str]] | Matcher
BodyContentMatcher = bytes | Matcher
CustomMatcher = Callable[[Request], Awaitable[bool]] | Callable[[Request], bool]
CustomHandler = Callable[[Request], Awaitable[Response | None]] | Callable[[Request], SyncResponse | None]
