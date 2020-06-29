# -*- coding: utf-8 -*-
"""
Common test functionality
(Copied from https://github.com/CITGuru/PyInquirer/blob/master/tests/helpers.py)
"""
from __future__ import print_function

import codecs
import os
import select
import sys
import time

import pytest
import regex
from prompt_toolkit.eventloop.posix import PosixEventLoop
from prompt_toolkit.input import PipeInput
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.output import DummyOutput
from ptyprocess import PtyProcess
from PyInquirer import prompts
from PyInquirer import style_from_dict
from PyInquirer import Token


# http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991
class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

        # use Bunch to create group of variables:
        # cf = Bunch(datum=y, squared=y*y, coord=x)


keys = Bunch(
    DOWN='\x1b[B',
    UP='\x1b[A',
    LEFT='\x1b[D',
    RIGHT='\x1b[C',
    ENTER='\x0a',  # ControlJ  (Identical to '\n')
    ESCAPE='\x1b',
    CONTROLC='\x03',
    SPACE='\x20',
    BACK='\x7f')


style = style_from_dict({
    Token.QuestionMark: '#FF9D00 bold',
    Token.Selected: '#5F819D bold',
    Token.Instruction: '',  # default
    Token.Answer: '#5F819D bold',
    Token.Question: '',
})


def remove_ansi_escape_sequences(text):
    # http://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
    # remove all ansi escape sequences
    # return regex.sub(r'(\x9b|\x1b\[)[0-?]*[ -\/]*[@-~]|[ ]*\r', '', text)
    text = regex.sub(r'(\x9b|\x1b\[)[0-?]*[ -\/]*[@-~]', '', text)
    text = regex.sub(r'[ \r]*\n', '\n', text)  # also clean up the line endings
    return text

# helper for running sut as subprocess within pty
# does two things
# * test app running in pty in subprocess
# * get test coverage from subprocess

# docu:
# http://blog.fizyk.net.pl/blog/gathering-tests-coverage-for-subprocesses-in-python.html


PY3 = sys.version_info[0] >= 3

if PY3:
    basestring = str


class SimplePty(PtyProcess):
    """Simple wrapper around a process running in a pseudoterminal.

    This class exposes a similar interface to :class:`PtyProcess`, but its read
    methods return unicode, and its :meth:`write` accepts unicode.
    """

    def __init__(self, pid, fd, encoding='utf-8', codec_errors='strict'):
        super(SimplePty, self).__init__(pid, fd)
        self.encoding = encoding
        self.codec_errors = codec_errors
        self.decoder = codecs.getincrementaldecoder(
            encoding)(errors=codec_errors)

    def read(self, size=1024):
        """Read at most ``size`` bytes from the pty, return them as unicode.

        Can block if there is nothing to read. Raises :exc:`EOFError` if the
        terminal was closed.

        The size argument still refers to bytes, not unicode code points.
        """
        b = super(SimplePty, self).read(size)
        if self.skip_cr:
            b = b.replace(b'\r', b'')
        # if self.skip_ansi:
        #    b = remove_ansi_escape_sequences(b)
        return self.decoder.decode(b, final=False)

    def write(self, s):
        """Write the unicode string ``s`` to the pseudoterminal.
        This intends to make tests a little less verbose.

        Returns the number of bytes written.
        """
        if isinstance(s, basestring):
            b = s.encode(self.encoding)
        count = super(SimplePty, self).write(b)
        return count

    def writeline(self, s):
        """Syntactic sugar to add a '\n' at the end of the .

        Returns the number of bytes written.
        """
        if not s.endswith('\n'):
            s += '\n'
        return self.write(s)

    @classmethod
    def spawn(
            cls, argv, cwd=None, env=None, echo=False, preexec_fn=None,
            dimensions=(24, 80), skip_cr=True, skip_ansi=True, timeout=1.0):
        """

        :param argv:
        :param cwd:
        :param env:
        :param echo: default is False so we do not have to deal with the echo
        :param preexec_fn:
        :param dimensions:
        :param skip_cr: skip carriage return '/r' characters when comparing equality
        :param skip_ansi: skip ansi escape sequences when comparing equality
        :param timeout: read timeout in seconds
        :return: subprocess handle
        """
        if env is None:
            env = os.environ
        inst = super(SimplePty, cls).spawn(argv, cwd, env, echo, preexec_fn,
                                           dimensions)
        inst.skip_cr = skip_cr
        inst.skip_ansi = skip_ansi
        inst.timeout = timeout  # in seconds
        return inst

    def expect(self, text):
        """Read until equals text or timeout."""
        # inspired by pexpect/pty_spawn and  pexpect/expect.py expect_loop
        end_time = time.time() + self.timeout
        buf = ''
        while (end_time - time.time()) > 0.0:
            # switch to nonblocking read
            reads, _, _ = select.select(
                [self.fd], [], [], end_time - time.time())
            if len(reads) > 0:
                try:
                    buf = remove_ansi_escape_sequences(buf + self.read())
                except EOFError:  # pragma: no cover
                    print('len: %d' % len(buf))
                    assert buf == text
                if buf == text:
                    return
                elif len(buf) >= len(text):  # pragma: no cover
                    break
            else:  # pragma: no cover
                # do not eat up CPU when waiting for the timeout to expire
                time.sleep(self.timeout/10)
        print(repr(buf))  # debug ansi code handling
        print(repr(text))
        assert buf == text


def create_example_fixture(example):
    """Create a pytest fixture to run the example in pty subprocess & cleanup.

    :param example: relative path like 'examples/input.py'
    :return: pytest fixture
    """
    @pytest.fixture
    def example_app():
        p = SimplePty.spawn(['python', example])
        yield p
        # it takes some time to collect the coverage data
        # if the main process exits too early the coverage data is not available
        time.sleep(p.delayafterterminate)
        try:
            p.sendintr()  # in case the subprocess was not ended by the test
        except OSError as e:  # pragma: no cover
            if e.errno != 5:
                raise
        p.wait()  # without wait() the coverage info never arrives
    return example_app
