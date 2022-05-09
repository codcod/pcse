"""WSGI apps based on extended Path Dispatchers."""

# required to implement WSGI applications
import abc
import re
import typing as tp
from urllib.parse import parse_qsl
from wsgiref.simple_server import make_server

# required to implement example webapps
from multiprocessing import Process
from time import ctime

Environ: tp.TypeAlias = dict[str, tp.Any]
Headers: tp.TypeAlias = list[tuple[str, str]]
StartResponse: tp.TypeAlias = tp.Callable[[str, Headers], None]
HandlerReturns: tp.TypeAlias = tp.Iterable[bytes]
Handler: tp.TypeAlias = tp.Callable[[Environ, StartResponse], HandlerReturns]


class WSGIApp(abc.ABC):
    """Base WSGI application.

    Provides implementation for `serve_forever`.
    """

    @abc.abstractmethod
    def register(self, method: str, path: str, handler: Handler) -> Handler:
        """Register a route with the application."""
        raise NotImplementedError()

    def notfound_404(
        self, environ: Environ, start_response: StartResponse
    ) -> HandlerReturns:
        """Reply in case of HTTP 404 error code, default handler."""
        headers = [('Content-Type', 'text/html')]
        start_response('404 Not Found', headers)
        return [b'<html><h1>404 Not Found</h1></html>']

    @abc.abstractmethod
    def __call__(
        self, environ: Environ, send_response: StartResponse
    ) -> HandlerReturns:
        """Call a handler registered under given method and path."""
        raise NotImplementedError()

    def serve_forever(self, port: int = 8001) -> None:
        """Serve the application under given port."""
        httpd = make_server('', port, self)  # type: ignore
        print('Serving on port %s...' % port)
        httpd.serve_forever()


class BasicWSGIApp(WSGIApp):
    """WSGI application based on `BasicPathDispatcher`."""

    def __init__(self) -> None:
        """Init."""
        self.routes: dict[tuple[str, str], Handler] = {}

    def register(self, method: str, path: str, handler: Handler) -> Handler:
        """Implement inherited method."""
        self.routes[method.upper(), path] = handler
        return handler

    def __call__(
        self, environ: Environ, send_response: StartResponse
    ) -> HandlerReturns:
        """Implement inherited method."""
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        params = parse_qsl(environ['QUERY_STRING'])
        environ['params'] = dict(params)
        handler = self.routes.get((method, path), self.notfound_404)
        return handler(environ, send_response)


class RegexWSGIApp(WSGIApp):
    """WSGI application based on `RegexPathDispatcher`."""

    def __init__(self) -> None:
        """Init."""
        self.routes: list[tuple[str, re.Pattern[tp.Any], Handler]] = []

    def register(self, method: str, path: str, handler: Handler) -> Handler:
        """Implement inherited method."""
        pattern = re.compile(path)
        self.routes.append((method.upper(), pattern, handler))
        return handler

    def __call__(
        self, environ: Environ, send_response: StartResponse
    ) -> HandlerReturns:
        """Implement inherited method."""
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        params = parse_qsl(environ['QUERY_STRING'])
        environ['params'] = dict(params)
        handler: Handler = self.notfound_404
        for method_, pattern, fn in self.routes:
            matched_path = pattern.fullmatch(path)
            if matched_path and method_ == method.upper():
                handler = fn
                environ['args'] = matched_path.groupdict()
                break
        return handler(environ, send_response)


#
# The following shows how to put the WSGI applications to a bit more
# realistic use
#

hello_tmpl = """\
<!doctype html>
<html lang="en">
    <head>
        <title>WSGIApp</title>
    </head>
    <body>
        <h1>Hello {name}</h1>
        <p>Zażółć gęślą jaźń.</p>
    </body>
</html>"""

user_tmpl = """\
<!doctype html>
<html lang="en">
    <head>
        <title>WSGIApp</title>
    </head>
    <body>
        <h2>User details</h2>
        <ul><li>name: {user[name]}</li>
        <li>id: {id}</li>
        <li>age: {user[age]}</li></ul>
    </body>
</html>"""


def time(environ: Environ, start_response: StartResponse) -> HandlerReturns:
    """Respond with current time."""
    headers = [('Content-Type', 'text/plain')]
    start_response('202 OK', headers)
    yield b'time is ' + ctime().encode()


def hello(environ: Environ, start_response: StartResponse) -> HandlerReturns:
    """Respond with `hello_tmpl` web page."""
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response('202 OK', headers)
    params = environ['params']
    resp = hello_tmpl.format(name=params.get('name'))
    yield resp.encode('utf-8')


def get_user(
    environ: Environ, start_response: StartResponse
) -> HandlerReturns:
    """Respond with `user_tmpl` web page."""
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    users = [{'name': 'John', 'age': 20}, {'name': 'Mary', 'age': 30}]
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response('202 OK', headers)
    id = int(environ['args'].get('id'))
    resp = user_tmpl.format(id=id, user=users[id])
    yield resp.encode('utf-8')


if __name__ == '__main__':
    """Create and run webapps based on both WSGI applications.

    Register one more route for `RegexWSGIApp`, as she can handle URL
    arguments, i.e. '/user/<id>'.

    Run both webapps in parallel on different ports:
    - http://localhost:8001/hello?name=john
    - http://localhost:8002/user/1
    """

    server_processes = []
    for i, app in enumerate([BasicWSGIApp(), RegexWSGIApp()]):
        app.register('GET', r'/time', time)
        app.register('GET', r'/hello', hello)

        if app.__class__ == RegexWSGIApp:
            app.register('GET', r'/user/(?P<id>\d+)', get_user)

        p = Process(target=app.serve_forever, args=(8001 + i,))
        p.start()
        server_processes.append(p)

    for server in server_processes:
        server.join()
