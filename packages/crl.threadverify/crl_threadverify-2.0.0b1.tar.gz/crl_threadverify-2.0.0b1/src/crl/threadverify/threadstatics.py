import threading
from io import StringIO
import datetime
from . dumptrace import DumpTrace


__copyright__ = 'Copyright (C) 2019, Nokia'


class StackItem(object):

    description = 'description'
    resource = 'file'

    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes

    def __str__(self):
        return '{resource}: {filename}, {description}: {name}'.format(
            resource=self.resource,
            filename=self.filename,
            description=self.description,
            name=self.name)

    @property
    def filename(self):
        return self.attributes.get('source')


class Keyword(StackItem):
    @property
    def description(self):
        return 'keyword'

    @property
    def filename(self):
        return self.attributes.get('libname')

    @property
    def resource(self):
        return 'resource'


class Testcase(StackItem):
    @property
    def description(self):
        return 'testcase'


class Suite(StackItem):

    @property
    def description(self):
        return 'suite'

    @property
    def source(self):
        return self.filename


class ThreadStatics(object):
    def __init__(self, thread):
        self.thread = thread
        self.robotstack = []
        self.parent = None
        self._start_header = ''
        self._robottraceatstart = ''
        self._backtraceatstart = ''
        self.indent = 2

    def start_suite(self, name, attributes):
        self.robotstack.append(Suite(name, attributes))

    def end_suite(self):
        self.robotstack.pop()

    def start_test(self, name, attributes):
        self.robotstack.append(
            Testcase(name,
                     self._get_attrs_with_source(attributes)))

    def end_test(self):
        self.robotstack.pop()

    def start_keyword(self, name, attributes):
        self.robotstack.append(Keyword(name, attributes))

    def end_keyword(self):
        self.robotstack.pop()

    def get_log(self):
        return '\n'.join([self._get_log(p) for p in self.parents_and_self()])

    @staticmethod
    def _get_log(parent):
        return '\n'.join(parent.log_items())

    def parents_and_self(self):
        for parent in self.parents():
            yield parent

        yield self

    def parents(self):
        if self.parent is not None:
            for parent in self.parent.threadverify_statics.parents():
                yield parent

            yield self.parent.threadverify_statics

    def log_items(self):
        return list(filter(
            None, [self._start_header,
                   self._robottraceatstart,
                   self._backtraceatstart]))

    def _get_attrs_with_source(self, attributes):
        attributes.update({
            'source': next(iter(reversed(self.robotstack))).source})
        return attributes

    def log_start(self):
        self.parent = threading.current_thread()
        self._set_start_header()
        if self.parent.threadverify_statics.robotstack:
            self._set_robotstackatstart()
        self._set_backtraceatstart()

    def _set_start_header(self):
        # pylint: disable=missing-format-attribute
        self._start_header = (
            '{thread.name} started by {parent.name} at {time}'.format(
                thread=self.thread,
                parent=self.parent,
                time=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]))

    def _set_robotstackatstart(self):
        self._robottraceatstart = (
            '\nRobot Framework Traceback (most recent call last):\n')
        self._robottraceatstart += '\n'.join([
            self.indent * ' ' + str(stackitem)
            for stackitem in self.parent.threadverify_statics.robotstack])
        self._robottraceatstart += '\n'

    def _set_backtraceatstart(self):
        with StringIO() as f:
            DumpTrace(f).dump_current_thread()
            self._backtraceatstart = f.getvalue()
