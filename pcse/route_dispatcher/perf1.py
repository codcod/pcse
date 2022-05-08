"""Simple performance tests for path dispatchers."""
# flake8: noqa

from pcse.route_dispatcher.dispatcher import BasicPathDispatcher, RegexPathDispatcher

def _timeit(cls, handler, count=10**4):
    import time

    how_many_routes = 50  # dispatcher will have this many routes registered

    disp = cls()
    for i in range(how_many_routes):
        disp.register('GET', f'/timeit_{i}', handler)

    route_first = f'/timeit_0'
    route_last = f'/timeit_{how_many_routes-1}'

    ts = time.monotonic()
    for _ in range(count):  # this is how many searches for a route will be run
        h = disp.call_route('GET', route_first)  # search a route registered first
        assert h==handler()
        h = disp.call_route('GET', route_last)   # search a route registered last
        assert h==handler()
    te = time.monotonic()
    res = te - ts
    print(f'  {res:.4f}')
    return res


def _main(cls1, cls2):
    import statistics as stat
    x = []
    y = []

    # how many time _timeit will be called (to calculate median from)
    how_many_repetitions = 15

    print(f'Route search times with the first router:')
    for _ in range(how_many_repetitions):
        x.append(_timeit(cls1, lambda: 'BasicPathDispatcher'))
    mx = stat.median(x)
    print(f'Median for "{cls1.__name__}" = ', mx)

    print(f'Route search times with the second router:')
    for _ in range(how_many_repetitions):
        y.append(_timeit(cls2, lambda: 'RegexPathDispatcher'))
    my = stat.median(y)
    print(f'Median for "{cls2.__name__}" = ', my)

    print(f'Diff: the slower algorithm is '
          f'{max(mx, my) / min(mx, my):.1f}x slower than the quicker one')


if __name__ == '__main__':
    _main(BasicPathDispatcher, RegexPathDispatcher)


# vim: sw=4:et:ai
