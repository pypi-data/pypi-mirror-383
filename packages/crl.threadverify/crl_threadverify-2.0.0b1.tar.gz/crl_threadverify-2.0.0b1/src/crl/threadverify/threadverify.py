from __future__ import print_function
import traceback
import sys
from contextlib import contextmanager
from . threadingmonkeypatch import ThreadingMonkeypatch
from . dumptrace import DumpTrace


__copyright__ = 'Copyright (C) 2019, Nokia'


class ThreadVerificationFailed(Exception):
    pass


class ThreadVerify(object):

    def __init__(self):
        self._threadingmonkeypatch = ThreadingMonkeypatch()

    @contextmanager
    def raise_and_dump_if_new_threads(self):
        with self._threadingmonkeypatch:
            with self._raise_if_needed():
                yield None

    @contextmanager
    def _raise_if_needed(self):
        try:
            try:
                yield None
            except Exception as e:
                print('{}: {}'.format(e.__class__.__name__, str(e)))
                print('Traceback:\n{}'.format(
                    ''.join(traceback.format_tb(sys.exc_info()[2]))))
                raise
        finally:
            self._if_new_raise_and_dump()

    def _if_new_raise_and_dump(self):
        try:
            next(self._threadingmonkeypatch.new_alive_threads())
            self._dump_threads_statics()
            raise ThreadVerificationFailed()
        except StopIteration:
            pass

    def _dump_threads_statics(self):
        for t in self._threadingmonkeypatch.new_alive_threads():
            print(
                'Still running thread: {t.name}\n\n'
                '{t.name} start traceback'
                ' (most recently started thread last):'.format(t=t))
            print(t.threadverify_statics.get_log())

        DumpTrace().dump()


@contextmanager
def verify_no_new_threads_at_end():
    """Contexmanager which verify that there is no new active threads after
    start. Prints to stdout information of still active threads:

      - Thread stack which lead starting of the new thread.

      - Robot Framework backtrace in case listener
        :class:`.ThreadListener` is used when *robot.run_cli()* is started.

      - Bcktrace dump of the current threads state.

    Raises:
      ThreadVerificationFailed: Raised if there is any new active
                                threads at exit of the context.

    Example::

      >>> import threading
      >>> import time
      >>> from crl.threadverify import verify_no_new_threads_at_end
      >>>
      >>> def work_forever():
      ...     while(True):
      ...         time.sleep(1)
      ...
      >>> thread = threading.Thread(target=work_forever)
      >>>
      >>> with verify_no_new_threads_at_end():
      ...     thread.start()
      ...
      Still running thread: Thread-1

      Thread-1 start traceback (most recently started thread last):

      Thread-1 started by MainThread at 11:48:14.471
      =================================================
      Traceback (most recent call last):
        File: "<stdin>", line 2, in <module>
            local variables:

       ...

                raise ThreadVerificationFailed()
        crl.threadverify.threadverify.ThreadVerificationFailed

    """
    with ThreadVerify().raise_and_dump_if_new_threads():
        yield None
