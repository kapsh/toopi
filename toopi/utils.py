"""Helper functions."""

import functools
import logging
import shutil
import subprocess
from typing import Generator, Iterable, List

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
    return f'# {command}\n\n{output}'


def tabulate(rows: List[Iterable[str]], *, gap=2, titles: List[str] = None
             ) -> Generator[str, None, None]:
    """Align fields from rows by width and add underlined header.

    Works only when titles and all items in rows have same length,
    throws ValueError otherwise.

    :param rows: table data.
    :param gap: space between columns.
    :param titles: column names.
    """
    if titles:
        header = [titles, ['‾' * len(field) for field in titles]]
        data = header + rows
    else:
        data = rows

    if len(set(map(len, data))) != 1:
        raise ValueError('Found rows with different length')

    col_widths = [
        max(map(len, column)) + gap
        for column in zip(*data)
    ]

    for row in data:
        yield ''.join(
            field.ljust(width)
            for field, width in zip(row, col_widths)
        ).rstrip()
