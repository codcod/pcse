"""Path dispatchers.

Path dispatcher dispatches (routes) requests to a registered handler based on
given set of arguments:

- method: 'GET', 'POST', etc. (HTTP methods)
- path: URL fragment like '/user/1', '/time'
"""

import re
from typing import Callable


class PathDispatcher:
    """Dispatch requests to a registered handler based on a given path and method.

    Base class indended for extension.
    """

    def register(self, method: str, path: str, handler: Callable):
        """Register route with the path dispatcher."""
        raise NotImplementedError()

    def route_notfound_404(self):
        """Handle route search misses."""
        print('Route not found')
        return '404 Not Found'

    def call_route(self, method, path):
        """Search route for a given set of parameters."""
        raise NotImplementedError()


class BasicPathDispatcher(PathDispatcher):
    """PathDispatcher implemented with a simple dictionary.

    Does not support paths with parameters.
    """

    def __init__(self):
        """Init."""
        self.routes = {}

    def register(self, method: str, path: str, handler: Callable):
        """Implement inherited method."""
        self.routes[method.upper(), path] = handler
        return handler

    def call_route(self, method, path):
        """Implement inherited method."""
        handler = self.routes.get((method, path), self.route_notfound_404)
        return handler()


class RegexPathDispatcher(PathDispatcher):
    """PathDispatcher implemented with regex to support paths with parameters.

    Much slower than `BasicPathDispatcher`.
    """

    def __init__(self):
        """Init."""
        self.routes = []

    def register(self, method: str, path: str, handler: Callable):
        """Implement inherited method."""
        pattern = re.compile(path)
        self.routes.append((method.upper(), pattern, handler))
        return handler

    def call_route(self, method, path):
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
