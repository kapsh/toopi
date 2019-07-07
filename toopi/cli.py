"""Command line interface and main logic flow."""

import argparse
import logging
import sys
from pathlib import Path

from . import __doc__ as description, paste, utils

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=description)

    opts = parser.add_argument_group('Paste options')
    opts.add_argument('-s', dest='service', choices=paste.SERVICES, default=paste.DEFAULT_SERVICE,
                      help='Set service to use. Default: %(default)s', metavar='SERVICE')
    opts.add_argument('-l', dest='language', default='text',
                      help='Language (affects highlight). Default: %(default)s')
    opts.add_argument('-e', dest='expiry', help='Expiration period')
    opts.add_argument('-t', dest='title', default='', help='Paste title (where available)')

    source = parser.add_argument_group(
        'Send text from', '(without any of these %(prog)s will read stdin)'
    ).add_mutually_exclusive_group()
    source.add_argument('-f', dest='file', type=Path, help='Paste content of this file')
    source.add_argument('-c', dest='command', help='Paste command with output')
    source.add_argument('-x', dest='from_clipboard', action='store_true',
                        help='Paste clipboard content')

    url = parser.add_argument_group('Resulting URL')
    url.add_argument('-r', dest='raw', action='store_true',
                     help='Get URL for raw content (without html and highlight)')
    url.add_argument('-X', dest='to_clipboard', action='store_true',
                     help='Copy URL to clipboard')

    query = parser.add_argument_group('Query options').add_mutually_exclusive_group()
    query.add_argument('-S', dest='list_services', action='store_true',
                       help='List known services')
    query.add_argument('-L', dest='list_languages', action='store_true',
                       help='List languages supported by chosen server')
    query.add_argument('-E', dest='list_expiries', action='store_true',
                       help='List expirations supported by chosen server')
    query.add_argument('-V', dest='version', action='store_true',
                       help='Show program version')

    parser.add_argument('-v', dest='verbose', action='store_true', help='Enable verbose logging',
                        default=True)  # TODO for now

    return parser.parse_args()


def main():
    """Entry point."""
    args = parse_args()
    init_logging(args.verbose)
    log.debug(f'Arguments: {args}')

    engine = paste.paste_engine(args.service)

    # instaexit options first
    if args.version:
        print_version()
        exit()
    if args.list_services:
        list_services()
        exit()
    if args.list_languages:
        list_languages(engine)
        exit()
    if args.list_expiries:
        list_expiries(engine)
        exit()

    command: str = args.command
    file: Path = args.file
    title: str = args.title

    try:
        # TODO split large data?
        if file:
            title = title or file.name
            with file.open() as source:
                text = source.read()
        elif command:
            title = title or command
            text = utils.command_with_output(command)
        elif args.from_clipboard:
            text = utils.clipboard_paste()
        else:
            title = title or 'stdin'
            text = sys.stdin.read()

        result = engine.post(
            text, title, args.language, args.expiry or engine.default_expiry)
        url = result.raw_url if args.raw else result.nice_url
        if args.to_clipboard:
            utils.clipboard_copy(url)
        print(url)

    except Exception as exc:  # pylint: disable=broad-except
        log.error(exc)
        exit(1)


def print_version():
    """Print program name and version."""
    from . import __version__, __name__ as name  # TODO ??
    print(name, __version__)


def init_logging(verbose=False):
    """Set logging format to something more readable."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')


def list_services():
    """Print known services."""
    info = list(sorted(paste.services_info().items()))
    for row in utils.tabulate(info, titles=['name', 'url']):
        print(row)


def list_languages(engine):
    """Print languages supported by service."""
    log.error(f'TODO cannot list languages for {engine}')


def list_expiries(engine):
    if engine.expiries:
        print(engine.expiries)
    else:
        log.error('Cannot list expiries for this service')
