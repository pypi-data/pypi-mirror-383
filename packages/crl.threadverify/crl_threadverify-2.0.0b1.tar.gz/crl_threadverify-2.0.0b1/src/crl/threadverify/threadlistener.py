import logging
import threading


__copyright__ = 'Copyright (C) 2019, Nokia'

logger = logging.getLogger(__name__)


class ThreadListener(object):
    """Robot Framework listener class to be used with
    :func:`.threadverify.verify_no_new_threads_at_end`.

    Example::

      >>> from robot import run_cli
      >>> from crl.threadverify import verify_no_new_threads_at_end
      >>> with verify_no_new_threads_at_end():
      ...     run_cli(['--listener', 'crl.threadverify.ThreadListener',
      ...              'robottests/newthreads.robot'])
      ...
      ===================================================================
      Newthreads
      ===================================================================
      New Threads                                                | PASS |
      -------------------------------------------------------------------
      Newthreads                                                 | PASS |
      1 critical test, 1 passed, 0 failed
      1 test total, 1 passed, 0 failed
      ===================================================================
      Output:  /home/pehuovin/crl-threadverify/tests/output.xml
      Log:     /home/pehuovin/crl-threadverify/tests/log.html
      Report:  /home/pehuovin/crl-threadverify/tests/report.html
      Still running thread: Thread-1

      Thread-1 start traceback (most recently started thread last):

      Thread-1 started by MainThread at 12:34:30.614
      Robot Framework Traceback (most recent call last):
        file: robottests/newthreads.robot, suite: Newthreads
        file: robottests/newthreads.robot, testcase: New Threads
        resource: CreateThread, keyword: CreateThread.Create Thread

      =================================================
      Traceback (most recent call last):
        File: "<stdin>", line 3, in <module>
      ...

          raise ThreadVerificationFailed()
      crl.threadverify.threadverify.ThreadVerificationFailed
    """

    ROBOT_LISTENER_API_VERSION = 2

    def start_suite(self, name, attributes):
        self._threadstatics.start_suite(name, attributes)

    def end_suite(self, *_):
        self._threadstatics.end_suite()

    def start_test(self, name, attributes):
        self._threadstatics.start_test(name, attributes)

    def end_test(self, *_):
        self._threadstatics.end_test()

    def start_keyword(self, name, attributes):
        self._threadstatics.start_keyword(name, attributes)

    def end_keyword(self, *_):
        self._threadstatics.end_keyword()

    @property
    def _threadstatics(self):
        return threading.current_thread().threadverify_statics
