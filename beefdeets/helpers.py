from functools import wraps
from typing import Callable, Type


def catch(*exceptions: Type[BaseException]) -> Callable[[Callable], Callable]:
    """Call a function, returning None if a given exception is raised."""
    def _decorator(func: Callable) -> Callable:
        @wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions:
                return None

        return _wrapper

    return _decorator
