from functools import wraps, update_wrapper
from typing import Callable, Type, Optional, TypeVar, Dict
import re

from flask import make_response
from werkzeug.wrappers import Response


def nocache(func: Callable[[], Response]) -> Callable[[], Response]:
    """Eliminate caching for a Flask route."""
    @wraps(func)
    def _wrapper() -> Response:
        resp = make_response(func())
        resp.cache_control.no_cache = True
        return resp

    return _wrapper


T = TypeVar("T")
Func = Callable[..., T]
OptFunc = Callable[..., Optional[T]]


def catch(*exceptions: Type[BaseException]) -> Callable[[Func], OptFunc]:
    """Call a function, returning None if a given exception is raised."""
    def _decorator(func: Func) -> OptFunc:
        @wraps(func)
        def _wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except exceptions:
                return None

        return _wrapper

    return _decorator


def parse_timestamp(timestamp: str) -> Optional[int]:
    """Parse a playback timestamp into a number of seconds.

    Expects the timestamp to be in HH:MM:SS or MM:SS format.
    """
    match = re.match(
        r"^(?:(?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)$", timestamp
    )

    if not match:
        return None

    time_fields = match.groupdict()
    return (
        int(time_fields["hours"] or 0) * 3600 +
        int(time_fields["minutes"]) * 60 +
        int(time_fields["seconds"])
    )
