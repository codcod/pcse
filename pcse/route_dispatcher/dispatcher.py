"""Path dispatchers.

Path dispatcher dispatches (routes) requests to a registered handler based on
given set of arguments:

- method: 'GET', 'POST', etc. (HTTP methods)
- path: URL fragment like '/user/1', '/time'
"""

import abc
import re
import typing as tp

Environ: tp.TypeAlias = dict[str, tp.Any]
Headers: tp.TypeAlias = list[tuple[str, str]]
StartResponse: tp.TypeAlias = tp.Callable[[str, Headers], None]
HandlerReturns: tp.TypeAlias = str
Handler: tp.TypeAlias = tp.Callable[[], HandlerReturns]


class PathDispatcher(abc.ABC):
    """Dispatch requests to a registered handler based on a given path and method.

    Base class indended for extension.
    """

    @abc.abstractmethod
    def register(self, method: str, path: str, handler: Handler) -> Handler:
        """Register route with the path dispatcher."""
        raise NotImplementedError()

    def route_notfound_404(self) -> HandlerReturns:
        """Handle route search misses."""
        print('Route not found')
        return '404 Not Found'

    @abc.abstractmethod
    def call_route(self, method: str, path: str) -> HandlerReturns:
        """Search route for a given set of parameters."""
        raise NotImplementedError()


class BasicPathDispatcher(PathDispatcher):
    """PathDispatcher implemented with a simple dictionary.

    Does not support paths with parameters.
    """

    def __init__(self) -> None:
        """Init."""
        self.routes: dict[tuple[str, str], Handler] = {}

    def register(self, method: str, path: str, handler: Handler) -> Handler:
        """Implement inherited method."""
        self.routes[method.upper(), path] = handler
        return handler

    def call_route(self, method: str, path: str) -> HandlerReturns:
        """Implement inherited method."""
        handler = self.routes.get((method, path), self.route_notfound_404)
        return handler()


class RegexPathDispatcher(PathDispatcher):
    """PathDispatcher implemented with regex to support paths with parameters.

    Much slower than `BasicPathDispatcher`.
    """

    def __init__(self) -> None:
        """Init."""
        self.routes: list[tuple[str, re.Pattern[tp.Any], Handler]] = []

    def register(self, method: str, path: str, handler: Handler) -> Handler:
        """Implement inherited method."""
        pattern = re.compile(path)
        self.routes.append((method.upper(), pattern, handler))
        return handler

    def call_route(self, method: str, path: str) -> HandlerReturns:
        """Implement inherited method."""
        handler = self.route_notfound_404
        for method_, pattern, fn in self.routes:
            match = pattern.fullmatch(path)
            if match and method_ == method.upper():
                handler = fn
                # params = match.groupdict()
                break
        return handler()


# vim: sw=4:et:ai
