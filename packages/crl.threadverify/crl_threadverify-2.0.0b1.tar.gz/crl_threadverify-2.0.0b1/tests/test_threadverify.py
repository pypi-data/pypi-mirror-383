from __future__ import print_function
import os
import re
import threading
import inspect
import importlib
from xml.etree import ElementTree
from collections import namedtuple
import pytest
from crl.threadverify import (
    verify_no_new_threads_at_end,
    ThreadVerificationFailed)
from robot import run_cli
from .robottests import CreateThread


__copyright__ = 'Copyright (C) 2019, Nokia'

original_start = threading.Thread.start

robottests = os.path.join(os.path.dirname(__file__), 'robottests')

robottestsnothreads = os.path.join(robottests, 'nothreads.robot')
robottestsnewthreads = os.path.join(robottests, 'newthreads.robot')
robottestscreatethread = os.path.join(robottests, 'CreateThread.py')
robottestsnewthreadsleavelast = os.path.join(robottests,
                                             'newthreadsleavelast.robot')
robottestscreateinloop = os.path.join(robottests, 'createinloop.robot')
robottestscreateinloopleaveone = os.path.join(robottests,
                                              'createinloopleaveone.robot')


class OriginalThread(namedtuple('OriginalThread', ['thread', 'start'])):
    pass


def threads():
    yield threading.Thread
    for t in threading.enumerate():
        yield t


def assert_original_thread():
    for t in threads():
        assert (inspect.getsource(t.start) ==
                inspect.getsource(original_start))
        with pytest.raises(AttributeError):
            print('Thread {t}: threadverify_statics: {stats}'.format(
                t=t, stats=t.threadverify_statics))


def test_threadverify_no_new_at_end():
    with verify_no_new_threads_at_end():
        assert not run_cli([robottestsnothreads], exit=False)

    assert_original_thread()


expected_robot_traceback_heading = (
    '\n\nRobot Framework Traceback (most recent call last):')


class RobotTrace(object):
    def __init__(self, filepath, name):
        self.filepath = filepath
        self.name = name

    @property
    def description(self):
        pass

    @property
    def line(self):
        return '  file: {filepath}, {description}: {name}'.format(
            filepath=self.filepath,
            description=self.description,
            name=self.name)


class KeywordTrace(RobotTrace):
    @property
    def description(self):
        return 'keyword'

    @property
    def line(self):
        return '  resource: {module}, {description}: {name}'.format(
            module=os.path.splitext(os.path.basename(self.filepath))[0],
            description=self.description,
            name=self.name)


class _TestcaseTrace(RobotTrace):
    @property
    def description(self):
        return 'testcase'


class SuiteTrace(RobotTrace):
    @property
    def description(self):
        return 'suite'


class ExpectedRobotTraceback(object):
    def __init__(self, *traces):
        self.traces = traces

    @property
    def traceback(self):
        return '{heading}\n{traces}'.format(
            heading=expected_robot_traceback_heading,
            traces='\n'.join(tr.line for tr in self.traces))


@pytest.fixture(scope='function')
def join_all(request):
    request.addfinalizer(CreateThread.CreateThread.join_all)


def test_threadverify_newthreads(capsys):
    with pytest.raises(ThreadVerificationFailed):
        with verify_no_new_threads_at_end():
            assert not run_cli(['--listener',
                                'crl.threadverify.ThreadListener',
                                '--loglevel',
                                'TRACE',
                                robottestsnewthreads], exit=False)

    out, _ = capsys.readouterr()
    filepathkwarg = {'filepath': robottestsnewthreads}
    ExpectedRobotTraceback(
        SuiteTrace(name='Newthreads', **filepathkwarg),
        _TestcaseTrace(name='New Threads', **filepathkwarg),
        KeywordTrace(name='CreateThread.Create Thread',
                     filepath=robottestscreatethread)).traceback in out
    assert 'wait_queue' in out
    assert_original_thread()


def test_threadverify_no_robot(capsys):
    with pytest.raises(ThreadVerificationFailed):
        with verify_no_new_threads_at_end():
            CreateThread.CreateThread().create_thread()
    out, _ = capsys.readouterr()
    print(out)
    assert 'in create_thread' in out
    assert 'Robot Framework Traceback' not in out


class RaisedException(Exception):
    pass


def test_threadverify_raise_no_new_threads(capsys):
    with pytest.raises(RaisedException) as excinfo:
        with verify_no_new_threads_at_end():
            raise RaisedException('message')

    assert str(excinfo.value) == 'message'
    out, _ = capsys.readouterr()
    assert 'RaisedException: message' in out


re_threadstillrunning = (
    "Still running thread: Thread-0\n\n"
    "Thread-0 start traceback \(most recently started thread last\):")


re_thread_backtrace = (
    "[0-2][0-9]:[0-5][0-9]:[0-5][0-9]\.[0-9]{3}\n"
    "[\s\S]+")


def get_re_backtrace(numberofthreads):
    for i in reversed(range(1, numberofthreads + 1)):
        yield '\nThread-{child} started by Thread-{parent} at '.format(
            child=i,
            parent=i + 1) + re_thread_backtrace


def get_re_backtraces(numberofthreads):
    return '\n'.join([bt for bt in get_re_backtrace(numberofthreads)])


def get_re_thread(numberofthreads):
    return (
        re_threadstillrunning + '\n' + get_re_backtraces(numberofthreads))


def create_threads_with_robot(numberofthreads):
    assert not run_cli(['--listener',
                        'crl.threadverify.ThreadListener',
                        '--loglevel',
                        'TRACE',
                        '--variable',
                        'numberofthreads:{}'.format(numberofthreads),
                        robottestsnewthreadsleavelast], exit=False)


def create_threads_without_robot(numberofthreads):
    CreateThread.CreateThread().create_threads_and_leave_last(numberofthreads)


def create_with_multiinheritance(numberofthreads):
    CreateThread.CreateThread().create_with_multiinheritance(numberofthreads)


def createfunctions():
    return pytest.mark.parametrize('createthreads', [
        create_threads_with_robot,
        create_threads_without_robot,
        create_with_multiinheritance])


def assert_robot_trace(out):
    assert re.search('file: .*/robottests/.+.robot, suite:.+',
                     out)
    assert re.search('file: .*/robottests/.+.robot, testcase:.+',
                     out)
    assert ('resource: CreateThread, keyword: '
            'CreateThread.Create Thread') in out


@createfunctions()
@pytest.mark.parametrize('numberofthreads', range(2, 4))
@pytest.mark.parametrize('replace_module', [True, False])
def test_threadverify_multiple_threads(capsys,
                                       numberofthreads,
                                       createthreads,
                                       replace_module):
    threading.current_thread().name = 'Thread-{}'.format(numberofthreads + 1)
    with pytest.raises(ThreadVerificationFailed):
        with verify_no_new_threads_at_end():
            if replace_module:
                importlib.reload(CreateThread)
            createthreads(numberofthreads)
    out, _ = capsys.readouterr()
    print(out)
    assert re.search(get_re_thread(numberofthreads), out)
    for i in range(1, numberofthreads):
        assert "'number_of_threads': {}".format(i) in out
    if createthreads == create_threads_with_robot:
        assert_robot_trace(out)


@pytest.mark.parametrize('iterations', range(2, 103, 100))
def test_threadverify_create_delete(iterations):
    with verify_no_new_threads_at_end():
        assert not run_cli(['--listener',
                            'crl.threadverify.ThreadListener',
                            '--variable',
                            'iterations:{}'.format(iterations),
                            robottestscreateinloop], exit=False)


@pytest.mark.parametrize('iterations', range(3, 104, 100))
def test_threadverify_create_delete_leave_one(
        capsys,
        join_all,  # pylint:disable=unused-argument
        iterations):
    with pytest.raises(ThreadVerificationFailed):
        with verify_no_new_threads_at_end():
            assert not run_cli(['--listener',
                                'crl.threadverify.ThreadListener',
                                '--variable',
                                'iterations:{}'.format(iterations),
                                robottestscreateinloopleaveone], exit=False)
    out, _ = capsys.readouterr()
    assert expected_robot_traceback_heading in out
    assert_no_errors_in_output_xml()


def assert_no_errors_in_output_xml():
    output_xml = os.path.join(os.getcwd(), 'output.xml')
    tree = ElementTree.parse(output_xml)
    root = tree.getroot()
    errors = root.find('errors')
    assert errors is None or errors.find('msg') is None
