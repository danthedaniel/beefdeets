from functools import wraps, update_wrapper
from typing import Callable, Type

from flask import make_response
from werkzeug.wrappers import Response


def nocache(func: Callable[[], Response]) -> Callable[[], Response]:
    """Eliminate caching for a Flask route."""
    @wraps(func)
    def _wrapper() -> Response:
        resp = make_response(func())
        resp.cache_control.no_cache = True
        return resp

    return update_wrapper(_wrapper, func)


def catch(*exceptions: Type[BaseException]) -> Callable[[Callable], Callable]:
    """Call a function, returning None if a given exception is raised."""
    def _decorator(func: Callable) -> Callable:
        @wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions:
                return None

        return update_wrapper(_wrapper, func)

    return _decorator
