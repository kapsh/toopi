"""Helper functions."""

import functools
import logging
import shutil
import subprocess

import requests

log = logging.getLogger(__name__)

try:
    import pyperclip
except ImportError:
    pyperclip = None


def strict_http_session() -> requests.Session:
    """Get new custom Session eager to raise errors."""
    session = requests.Session()
    session.request = functools.partial(session.request, timeout=30)  # TODO configurable
    session.hooks = {
        'response': lambda r, *a, **kw: r.raise_for_status(),
    }
    return session


def clipboard_copy(text: str) -> None:
    """Copy text to clipboard."""
    if pyperclip:
        pyperclip.copy(text)
    elif shutil.which('xclip'):
        subprocess.run(
            ['xclip', '-in', '-selection', 'clipboard'],
            input=text, text=True, check=True)
    else:
        raise RuntimeError('No way to copy')


def clipboard_paste() -> str:
    """Get text from clipboard."""
    if pyperclip:
        return pyperclip.paste()
    if shutil.which('xclip'):
        return subprocess.run(
            ['xclip', '-out', '-selection', 'clipboard'],
            capture_output=True, text=True, check=True
        ).stdout
    raise RuntimeError('No way to paste')


def command_with_output(command: str) -> str:
    """Run command and return it's text with output."""
    output = subprocess.run(
        command, shell=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    ).stdout
    return f'> {command}\n\n{output}'
