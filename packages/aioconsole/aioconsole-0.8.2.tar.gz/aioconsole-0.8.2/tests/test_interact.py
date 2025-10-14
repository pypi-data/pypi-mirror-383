import io
import os
import platform
import sys
import signal
import asyncio
from unittest.mock import Mock
from contextlib import contextmanager

import pytest
import pytest_asyncio
from aioconsole import interact
from aioconsole.stream import NonFileStreamReader, NonFileStreamWriter


@contextmanager
def stdcontrol(monkeypatch):
    # PS1
    monkeypatch.setattr("sys.ps1", "[Hello!]", raising=False)
    # Stdin control
    stdin_read, stdin_write = os.pipe()
    monkeypatch.setattr("sys.stdin", open(stdin_read))
    writer = NonFileStreamWriter(open(stdin_write, "w"))
    # Stdout control
    monkeypatch.setattr(sys, "stdout", io.StringIO())
    # Stderr control
    stderr_read, stderr_write = os.pipe()
    monkeypatch.setattr("sys.stderr", open(stderr_write, "w"))
    reader = NonFileStreamReader(open(stderr_read))
    # Yield
    yield reader, writer
    # Check
    assert sys.stdout.getvalue() == ""


async def assert_stream(stream, expected, loose=False):
    s = None if loose else "\n"
    for expected_line in expected.splitlines():
        line = await stream.readline()
        assert expected_line.strip(s) == line.decode().strip(s)


@pytest_asyncio.fixture(params=["unix", "not-unix"])
async def signaling(request, monkeypatch):
    if request.param == "not-unix":
        event_loop = asyncio.get_running_loop()
        m = Mock(side_effect=NotImplementedError)
        monkeypatch.setattr(event_loop, "add_signal_handler", m)
        monkeypatch.setattr(event_loop, "remove_signal_handler", m)
    yield request.param


@pytest.mark.asyncio
async def test_interact_simple(monkeypatch):
    with stdcontrol(monkeypatch) as (reader, writer):
        banner = "A BANNER"
        writer.write("1+1\n")
        await writer.drain()
        writer.stream.close()
        await interact(banner=banner, stop=False)
        await assert_stream(reader, banner)
        await assert_stream(reader, sys.ps1 + "2")
        await assert_stream(reader, sys.ps1)


@pytest.mark.asyncio
async def test_interact_traceback(monkeypatch):
    with stdcontrol(monkeypatch) as (reader, writer):
        banner = "A BANNER"
        writer.write("1/0\n")
        await writer.drain()
        writer.stream.close()
        await interact(banner=banner, stop=False)
        # Check stderr
        await assert_stream(reader, banner)
        await assert_stream(reader, sys.ps1 + "Traceback (most recent call last):")
        # Skip 3 lines
        for _ in range(4 if sys.version_info >= (3, 11) else 3):
            await reader.readline()
        # Check stderr
        await assert_stream(reader, "ZeroDivisionError: division by zero")
        await assert_stream(reader, sys.ps1)


@pytest.mark.asyncio
async def test_interact_syntax_error(monkeypatch):
    with stdcontrol(monkeypatch) as (reader, writer):
        writer.write("a b\n")
        await writer.drain()
        writer.stream.close()
        banner = "A BANNER"
        await interact(banner=banner, stop=False)
        await assert_stream(reader, banner)
        # Skip line
        await reader.readline()
        await assert_stream(reader, "    a b")
        if sys.version_info >= (3, 10, 0) and sys.version_info < (3, 10, 1):
            await assert_stream(reader, "    ^^^", loose=True)
        else:
            await assert_stream(reader, "      ^", loose=True)
        if (
            sys.version_info >= (3, 10, 0)
            and sys.version_info < (3, 10, 1)
            or (
                platform.python_implementation() == "PyPy"
                and sys.version_info >= (3, 9)
                and sys.version_info < (3, 10)
            )
        ):
            await assert_stream(
                reader, "SyntaxError: invalid syntax. Perhaps you forgot a comma?"
            )
        else:
            await assert_stream(reader, "SyntaxError: invalid syntax")
        await assert_stream(reader, sys.ps1)


@pytest.mark.asyncio
async def test_interact_keyboard_interrupt(monkeypatch, signaling):
    with stdcontrol(monkeypatch) as (reader, writer):
        # Start interaction
        banner = "A BANNER"
        task = asyncio.ensure_future(interact(banner=banner, stop=False))
        # Wait for banner
        await assert_stream(reader, banner)
        # Send SIGINT
        if sys.platform == "win32":
            signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
        else:
            os.kill(os.getpid(), signal.SIGINT)
        # Wait for ps1
        await assert_stream(reader, sys.ps1)
        await assert_stream(reader, "KeyboardInterrupt")
        # Close stdin
        writer.stream.close()
        # Wait for interact to finish
        await assert_stream(reader, sys.ps1)
        await task
        # Test
        assert sys.stdout.getvalue() == ""


@pytest.mark.asyncio
async def test_broken_pipe(monkeypatch, signaling):
    with stdcontrol(monkeypatch) as (reader, writer):
        # Start interaction
        banner = "A BANNER"
        task = asyncio.ensure_future(interact(banner=banner, stop=False))
        # Wait for banner
        await assert_stream(reader, banner)
        # Close stdin
        writer.stream.close()
        reader.stream.close()
        # Wait for interact to finish
        await task
        # Test
        assert sys.stdout.getvalue() == ""


@pytest.mark.asyncio
async def test_interact_multiple_indented_lines(monkeypatch):
    with stdcontrol(monkeypatch) as (reader, writer):
        banner = "A BANNER"
        writer.write("def x():\n    print(1)\n    print(2)\n\nx()\n")
        await writer.drain()
        writer.stream.close()
        await interact(banner=banner, stop=False)
        await assert_stream(reader, banner)
        await assert_stream(reader, sys.ps1 + sys.ps2 * 3 + sys.ps1 + "1\n2")


@pytest.mark.asyncio
async def test_interact_cancellation(monkeypatch):
    with stdcontrol(monkeypatch) as (reader, writer):
        banner = "A BANNER"
        task = asyncio.ensure_future(interact(banner=banner, stop=False))
        # Wait for banner
        await assert_stream(reader, banner)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert task.cancelled
