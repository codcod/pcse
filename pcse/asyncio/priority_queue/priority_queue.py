"""Async PriorityQueue hands-on."""
import argparse
import asyncio
import dataclasses as dtc
import logging
import time
import tracemalloc
import typing as tp
import uvloop
# from memory_profiler import profile

ItemInQueue: tp.TypeAlias = tuple[int, 'Item']


@dtc.dataclass
class Item:
    """Item stored in the queue."""

    # pylint: disable=too-few-public-methods
    name: str
    prio: int

    def astuple(self) -> ItemInQueue:
        """Represent Item as a tuple, which helps storing it in the queue."""
        return self.prio, self


async def process(item: Item) -> None:
    """Process the item taken from the queue."""
    logging.debug('[process] processing item=%s', item)


async def producer(
    queue: asyncio.PriorityQueue[ItemInQueue], count: int = 10**6
) -> None:
    """Produce items and puts them in the queue."""
    logging.warning('[producer] start producing')
    for i in range(count):
        if i % 10:
            item = Item('five', 5)
            logging.info('[producer<-] producing i=%i, item=%s:', i, item)
            await queue.put(item.astuple())
        else:
            item = Item('one', 1)
            logging.info('[producer<-] producing i=%i, item=%s:', i, item)
            await queue.put(item.astuple())
        await asyncio.sleep(0)
logging.warning('[producer] finished producing')


async def consumer(queue: asyncio.PriorityQueue[ItemInQueue]) -> None:
    """Consume items from the queue and initiates processing them."""
    logging.warning('[consumer] start consuming')
    while True:
        _, item = await queue.get()
        await process(item)
        queue.task_done()
        logging.info('[<-consumer] consumed item=%s', item)


async def main(count: int, sleep: int = 3) -> None:
    """Run main program."""
    # pylint: disable=invalid-name
    q: asyncio.PriorityQueue[ItemInQueue] = asyncio.PriorityQueue(count)
    how_many = int(count / PRODUCERS)
    producers = [asyncio.create_task(producer(q, how_many))
                 for _ in range(PRODUCERS)]
    logging.warning('[main] waiting %i second(s) before consuming', sleep)
    await asyncio.sleep(sleep)
    consumers = [asyncio.create_task(consumer(q)) for _ in range(CONSUMERS)]

    # wait for all producers to finish:
    await asyncio.gather(*producers)
    logging.warning('[main] all producer(s) finished their job')

    # wait for all tasks are consumed (all consumers are finished):
    await q.join()
    logging.warning('[main] all items from the queue'
                    'have been processed q.qsize()=%i', q.qsize())

    # all consumers are idle, no reason to keep them:
    for c in consumers:
        c.cancel()


parser = argparse.ArgumentParser()
parser.add_argument(
    '-l', '--log-level', type=str, default='warning',
    help='log level (debug, info, warn)'
)
parser.add_argument(
    '--count', type=int, default=10 ** 6,
    help='number of messages to publish'
)
parser.add_argument(
    '--producers', type=int, default=1,
    help='how many producers to create'
)
parser.add_argument(
    '--consumers', type=int, default=1,
    help='how many consumers to create'
)
parser.add_argument(
    '-s', '--sleep', type=int, default=3,
    help='seconds of delay between producing and consuming'
)
parser.add_argument(
    '--uvloop', action='store_true',
    help='use uvloop'
)
args = parser.parse_args()

PRODUCERS = args.producers
CONSUMERS = args.consumers

match args.log_level:
    case 'debug': LEVEL = logging.DEBUG
    case 'info': LEVEL = logging.INFO
    case 'warning': LEVEL = logging.WARNING
    case _: LEVEL = logging.ERROR

FORMAT = '%(asctime)s:%(name)s:%(levelname)s - %(message)s'
logging.basicConfig(level=LEVEL, format=FORMAT)

if args.uvloop: uvloop.install()  # pylint: disable=C0321 # noqa: E701

tracemalloc.start()
ts = time.monotonic()
logging.warning('[root] start measuring time ts=%f', ts)

logging.warning('[root] start event loop')
asyncio.run(main(args.count, args.sleep))
logging.warning('[root] finished event loop')

te = time.monotonic()
logging.warning('[root] finished measuring time te=%f', te)

size_, peak_ = tracemalloc.get_traced_memory()
size = size_ / 1024
peak = peak_ / 1024 / 1024
tracemalloc.stop()
logging.error('[root] Memory used: size=%.1fKiB, peak=%.1fMiB', size, peak)
logging.error('[root] Time spent: %.2fsec', te - ts)

# $ python async_priority_queue.py \
#          --sleep=1 \
#          --uvloop \
#          --producers=1 --consumers=1 \
#          --count=12 \
#          --log-level=debug
