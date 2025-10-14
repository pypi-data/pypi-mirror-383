import threading
from threading import Lock
from . threadstatics import ThreadStatics

__copyright__ = 'Copyright (C) 2019, Nokia'


class OperationRunner(object):

    def __init__(self):
        self._lock = Lock()
        self._running = False
        self._count = 0

    def run(self, operation):
        if self._prepare_run_and_get_need_with_lock():
            self._try_to_run_operation(operation)

    def _try_to_run_operation(self, operation):
        try:
            operation()
        finally:
            with self._lock:
                self._running = False

    def _prepare_run_and_get_need_with_lock(self):
        with self._lock:
            return self._prepare_run_and_get_need()

    def _prepare_run_and_get_need(self):
        self._count += 1
        if not self._count % 10 and not self._running:
            self._running = True
            return True
        return False


class ThreadingMonkeypatch(object):

    def __init__(self):
        self.threads_at_start = None
        self.started_threads = list()
        self.operationrunner = OperationRunner()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        self.threads_at_start = list(threading.enumerate())
        self._set_threadclasses()
        self._set_original_starts()
        self._set_started_threads()
        self._monkeypatch()

    def _set_threadclasses(self):
        self._threadclasses = set()
        self._add_to_threadclasses(threading.Thread)

    def _set_original_starts(self):
        self._original_starts = dict()
        for cls in self._threadclasses:
            self._original_starts[cls] = cls.start

    def _set_started_threads(self):
        self.started_threads = list()

    def _add_to_threadclasses(self, cls):
        for subcls in cls.__subclasses__():
            self._add_to_threadclasses(subcls)
        self._threadclasses.add(cls)

    def _monkeypatch(self):
        for t in self.threads_at_start:
            t.threadverify_statics = ThreadStatics(t)
        for threadcls in self._threadclasses:
            self._monkeypatch_threadcls(threadcls)

    def _monkeypatch_threadcls(self, threadcls):

        def start_with_statics(cls):
            cls.threadverify_statics = ThreadStatics(cls)
            self._original_starts[threadcls](cls)
            cls.threadverify_statics.log_start()
            self.started_threads.append(cls)
            self._cleanup_dead_if_needed()

        threadcls.start = start_with_statics

    def _cleanup_dead_if_needed(self):
        self.operationrunner.run(self._cleanup_dead)

    def _cleanup_dead(self):
        self.started_threads = [
            t for t in self.started_threads if t.is_alive()]

    def stop(self):
        for threadcls in self._threadclasses:
            threadcls.start = self._original_starts[threadcls]
        for t in set(self.started_threads + self.threads_at_start):
            delattr(t, 'threadverify_statics')

    def new_alive_threads(self):
        for t in self.started_threads:
            if t.is_alive():
                yield t
