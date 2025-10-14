from __future__ import print_function
import sys
import threading
import inspect


__copyright__ = 'Copyright (C) 2019, Nokia'


def dump_io():
    return sys.stdout


class DumpTrace(object):
    """Dump stacktrace of all saved active threads to *out*.
    The ideas are based on https://gist.github.com/737056."""

    def __init__(self, out=None, sepchr='=', seplen=49):
        self.out = dump_io() if out is None else out
        self.sep = sepchr * seplen

    def dprint(self, data):
        print(self._convert_to_unicode(data), file=self.out)

    @staticmethod
    def _convert_to_unicode(data):
        try:
            return unicode(data)
        except NameError:
            return data

    @staticmethod
    def frames():
        return sys._current_frames()

    @staticmethod
    def tmap():
        # get a map of threads by their ID so we can print their names
        # during the traceback dump
        return {t.ident: t for t in threading.enumerate()}

    def dump(self):
        self.dprint('Stack dump of all the threads')
        self.dprint(self.sep)
        for tid, frame in self.frames().items():
            self._dump_thread_if_not_junk(tid, frame)

    def dump_current_thread(self):
        for tid, frame in self.frames().items():
            if tid == threading.current_thread().ident:
                self.dprint(self.sep)
                self._dump_backtrace(frame)

    def _dump_thread_if_not_junk(self, tid, frame):
        thread = self.tmap().get(tid)
        if thread is not None:
            self._dump_thread(thread, frame)
            self.dprint('')

    def _dump_thread(self, thread, frame):
        self.dprint('{0.name}'.format(thread))
        self.dprint(self.sep)
        self._dump_backtrace(frame)

    def _dump_backtrace(self, frame):
        self.dprint('Traceback (most recent call last):')
        for outer in reversed(inspect.getouterframes(frame)):
            self._dump_frameinfo(outer[0])
            self._dump_frame_locals(outer[0])

    def _dump_frameinfo(self, frame):
        f = inspect.getframeinfo(frame)
        self.dprint(
            '  File: "{f.filename}",'
            ' line {f.lineno}, in {f.function}'.format(f=f))
        self._dump_code_if_exists(f)

    def _dump_code_if_exists(self, frameinfo):
        if frameinfo.code_context:
            self.dprint('    {code}'.format(
                code=frameinfo.code_context[0].strip()))

    @staticmethod
    def _strip(s):
        return s.strip('\n\r\t ')

    def _dump_frame_locals(self, frame, indent=6):
        self.dprint('{}local variables:'.format(' ' * indent))
        for n, v in frame.f_locals.items():
            try:
                self.dprint("{indent}'{n}': {v}".format(
                    indent=' ' * (indent + 2), n=n, v=repr(v)))
            except AttributeError as e:
                self.dprint(
                    "{indent}skipping variable value of '{n}' :{e}".format(
                        indent=' ' * (indent + 2),
                        n=n,
                        e=e))
