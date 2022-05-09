# Route dispatchers and WSGI apps

Source code: [dispatcher.py](../../pcse/route_dispatcher/dispatcher.py)

Source code: [wsgiapp.py](../../pcse/route_dispatcher/wsgiapp.py)

Basic "route dispatcher", or "path dispatcher" or just "router" that allows to
register a route and subsequently search for such a route can be implemented
with a dict:

```python
class Router:
    def __init__(self):
        self.routes: dict[tuple[str, str], Callable] = {}

    def register(self, method: str, path: str, handler: Callable):
        self.routes[method.upper(), path] = handler
        return handler

    def call_route(self, method: str, path: str) -> str:
        handler = self.routes.get((method, path), self.route_notfound_404)
        return handler()

    def route_notfound_404(self) -> str:
        return '404 Not Found'
```

This router can be called in a following way:

```python
r = Router()
r.register('GET', '/hello', lambda: 'hello has been called')

assert 'hello has been called' == r.call_route('GET', '/hello')
assert '404 Not Found' == r.call_route('POST', '/hello')
assert '404 Not Found' == r.call_route('GET', '/hello_world')
```

Next such a router can be quite easily extended and turned into a full-fledged ;-)
WSGI application.

```python
class WSGIApp:
    def __init__(self):
        self.routes: dict[tuple[str, str], Callable] = {}

    def register(self, method: str, path: str, handler: Callable) -> Callable:
        self.routes[method.upper(), path] = handler
        return handler

    def __call__(
        self, environ: dict, send_response: Callable
    ) -> Iterable[bytes]:
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        params = parse_qsl(environ['QUERY_STRING'])
        environ['params'] = dict(params)
        handler = self.routes.get((method, path), self.notfound_404)
        return handler(environ, send_response)

    def notfound_404(
        self, environ: dict, start_response: Callable
    ) -> Iterable[bytes]:
        headers = [('Content-Type', 'text/html')]
        start_response('404 Not Found', headers)
        return [b'<html><h1>404 Not Found</h1></html>']

    def serve_forever(self, port=8001):
        httpd = make_server('', port, self)
        print('Serving on port %s...' % port)
        httpd.serve_forever()
```

The following code sample shows how to write a handler, register it and start
serving the application with a refernce HTTP server.

```python
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


def time(environ: dict, start_response: Callable) -> Iterable[bytes]:
    headers = [('Content-Type', 'text/plain')]
    start_response('202 OK', headers)
    yield b'time is ' + ctime().encode()

def hello(environ: dict, start_response: Callable) -> Iterable[bytes]:
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response('202 OK', headers)
    params = environ['params']
    resp = hello_tmpl.format(name=params.get('name'))
    yield resp.encode('utf-8'

app = WSGIApp()
app.register('GET', r'/time', time)
app.register('GET', r'/hello/', hello)
app.serve_forever()
```

To make sure it works open web browser with the address:

```shell
$ open http://localhost:8001/hello?name=John
```
