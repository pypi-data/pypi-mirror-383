import threading
import logging
from queue import Queue


__copyright__ = 'Copyright (C) 2019, Nokia'

logger = logging.getLogger(__name__)


class _CreateThread(threading.Thread):

    def __init__(self, target=None, args=None):
        super(_CreateThread, self).__init__(
            target=self.wait_queue if target is None else target,
            args=[] if args is None else args)
        self.queue = Queue()

    def wait_queue(self):
        self.queue.get()


class _ACreateThread(_CreateThread):
    pass


class _BCreateThread(_CreateThread):
    pass


class _MultiinheritanceCreateThread(_ACreateThread, _BCreateThread):
    pass


class _RecursiveThread(object):

    def __init__(self, number_of_threads, threadcls=None):
        self.threadcls = threadcls or _CreateThread
        self.thread = self.threadcls(
            self.create_thread, args=[number_of_threads])
        self.thread.name = 'Thread-{}'.format(number_of_threads)

    def create_thread(self, number_of_threads):
        if number_of_threads:
            thread = _RecursiveThread(number_of_threads - 1,
                                      threadcls=self.threadcls)
            if number_of_threads == 1:
                thread.thread.daemon = True
            thread.thread.start()
            if number_of_threads > 1:
                thread.thread.join()
        else:
            self.thread.queue.get()

    def start_with_join(self):
        self.thread.start()
        self.thread.join()


class CreateThread(object):

    def __init__(self):
        self.queue = Queue()

    @staticmethod
    def create_thread():
        thread = _CreateThread()
        thread.start()

    @staticmethod
    def create_threads_and_leave_last(number_of_threads):
        _RecursiveThread(int(number_of_threads)).start_with_join()

    @staticmethod
    def create_with_multiinheritance(number_of_threads):
        _RecursiveThread(
            int(number_of_threads),
            threadcls=_MultiinheritanceCreateThread).start_with_join()

    def create_threads_in_loop(self, iterations):
        iterations = int(iterations)
        for _ in range(iterations):
            thread = self._create_thread_with_queue()
            self.queue.put(None)
            thread.join()

    def create_threads_in_loop_leave_one(self, iterations):
        iterations = int(iterations)
        self.create_threads_in_loop(iterations / 2)
        _CreateThread().start()
        self.create_threads_in_loop(iterations / 2)

    def _create_thread_with_queue(self):
        thread = threading.Thread(target=self._get_queue)
        thread.start()
        return thread

    def _get_queue(self):
        self.queue.get()

    @staticmethod
    def join_all():
        for t in threading.enumerate():
            try:
                t.queue.put(None)
            except AttributeError:
                pass
