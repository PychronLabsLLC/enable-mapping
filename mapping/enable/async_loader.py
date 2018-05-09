
import asyncore
import socket
from threading import Event, Thread
from time import time as _time

from six.moves import queue

from traits.api import HasTraits, Any, Instance


class AsyncLoader(HasTraits):

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_signal.set()
        self._thread.join()

    def put(self, request):
        self._queue.put(request)

    # Private interface ##################################################

    _thread = Any
    _stop_signal = Any
    _queue = Instance(queue.Queue)

    def __thread_default(self):
        return RequestingThread(self._queue, self._stop_signal)

    def __queue_default(self):
        return AsyncRequestQueue()

    def __stop_signal_default(self):
        return Event()


class RequestingThread(Thread):
    def __init__(self, queue, stop_signal):
        super(RequestingThread, self).__init__()
        self.queue = queue
        self.stop_signal = stop_signal
        self.daemon = True

    def run(self):
        # Wait for any requests
        while not self.stop_signal.is_set():
            try:
                # Block if there are no pending asyncore requests
                block = len(asyncore.socket_map) == 0
                reqs = self.queue.get_all(block=block, timeout=1.0)
                for req in reqs:
                    try:
                        req.connect()
                    except socket.gaierror:
                        # Don't panic, the server is not available
                        pass

            except queue.Empty:
                pass
            asyncore.loop()


class AsyncRequestQueue(queue.LifoQueue):
    def get_all(self, block=True, timeout=None):
        """Remove and return all items from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a positive number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """
        self.not_empty.acquire()
        try:
            if not block:
                if not self._qsize():
                    raise queue.Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a positive number")
            else:
                endtime = _time() + timeout
                while not self._qsize():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise queue.Empty
                    self.not_empty.wait(remaining)
            items = self._get_all()
            self.not_full.notify()
            return items
        finally:
            self.not_empty.release()

    def _get_all(self):
        all = self.queue[:]
        self.queue = []
        return all


#: Global async_loader instance. Use get_global_async_loader
#: to request this instance.
_async_loader = None


def get_global_async_loader():
    """
    Get the current global AsyncLoader instance,
    creating and initializing it if necessary.
    """
    global _async_loader
    if _async_loader is None:
        async_loader = AsyncLoader()
        async_loader.start()
        _async_loader = async_loader
    return _async_loader
