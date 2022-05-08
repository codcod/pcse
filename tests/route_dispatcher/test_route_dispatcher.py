import unittest
from pcse.route_dispatcher.dispatcher import *

def time():
    print('time handler called')
    return 'time'

def echo():
    print('echo handler called')
    return 'echo'


class TestDispatcher(unittest.TestCase):

    def setUp(self) -> None:
        self.bd = BasicPathDispatcher()
        self.rd = RegexPathDispatcher()

        for d in [self.bd, self.rd]:
            d.register('GET', r'/time', time)
            d.register('GET', r'/echo/(?P<id>\d+)', echo)
            d.register('GET', r'/echo', echo)

    def test_dispatcher_basic(self):
        d = self.bd
        not_found = '404 Not Found'
        self.assertEqual('time', d.call_route('GET', r'/time'))
        self.assertEqual('echo', d.call_route('GET', r'/echo'))
        self.assertEqual(not_found, d.call_route('POST', r'/echo'))
        self.assertEqual(not_found, d.call_route('POST', r'/echo/2'))
        self.assertEqual(not_found, d.call_route('GET', r'/echo/2'))

    def test_dispatcher_regex(self):
        d = self.rd
        not_found = '404 Not Found'
        self.assertEqual('time', d.call_route('get', r'/time'))
        self.assertEqual('echo', d.call_route('get', r'/echo'))
        self.assertEqual(not_found, d.call_route('post', r'/echo'))
        self.assertEqual(not_found, d.call_route('post', r'/echo/2'))
        self.assertEqual('echo', d.call_route('get', r'/echo/2'))

    def test_dispatcher_regex_routes_order(self):
        d = self.rd
        not_found = '404 not found'

        d.register('GET', r'/order', lambda: 'order')
        d.register('GET', r'/order/(?P<id>\d+)', lambda: 'order/id')

        self.assertEqual('order/id', d.call_route('get', r'/order/1'))
        self.assertEqual('order', d.call_route('get', r'/order'))

if __name__ == '__main__':
    unittest.main()


# vim: sw=4:et:ai
