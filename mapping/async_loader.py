from abc import ABCMeta, abstractmethod
from threading import Event, Thread

from six import with_metaclass
from six.moves import queue

from traits.api import HasTraits, Any, Instance


class AsyncLoader(HasTraits):
    """ A class which executes generic 'request' objects off of the main thread
    """

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
        return queue.Queue()

    def __stop_signal_default(self):
        return Event()


class AsyncRequest(with_metaclass(ABCMeta, object)):
    """ Interface for requests processed by AsyncLoader """

    @abstractmethod
    def execute(self):
        """ Run the request
        """


class RequestingThread(Thread):
    def __init__(self, queue_, stop_signal):
        super(RequestingThread, self).__init__()
        self.queue = queue_
        self.stop_signal = stop_signal
        self.daemon = True

    def run(self):
        # Wait for any requests
        while not self.stop_signal.is_set():
            try:
                # Use a timeout so that `self.stop_signal` controls our exit
                req = self.queue.get(block=True, timeout=1.0)
                req.execute()
            except queue.Empty:
                pass


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
