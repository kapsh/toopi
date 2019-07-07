"""Actual work with pastebins."""

import logging
from dataclasses import dataclass
from typing import Dict, Type
from urllib.parse import urljoin

from . import utils

log = logging.getLogger(__name__)


@dataclass
class PasteResult:  # TODO enum?
    nice_url: str
    raw_url: str


class PasteEngine:
    def __init__(self, domain: str):
        self.domain = domain

    def post(self, text, title, language, expiry) -> PasteResult:
        pass


class Pinnwand(PasteEngine):
    def post(self, text, title, language='text', expiry='1week') -> PasteResult:
        with utils.strict_http_session() as session:
            response = session.post(
                urljoin(self.domain, '/json/new'),
                data=dict(code=text, lexer=language, expiry=expiry))
        paste_id = response.json()['paste_id']
        return PasteResult(
            urljoin(self.domain, f'/show/{paste_id}'),
            urljoin(self.domain, f'/raw/{paste_id}'))


@dataclass
class ServiceInfo:
    domain: str
    engine: Type[PasteEngine]


SERVICES = {
    'local': ServiceInfo('http://localhost:8000/', Pinnwand),  # TODO move to config
    'bpaste': ServiceInfo('https://bpaste.net/', Pinnwand),
}

DEFAULT_SERVICE = 'local'


def paste_engine(service_code: str) -> PasteEngine:
    service = SERVICES[service_code]
    return service.engine(service.domain)


def get_services() -> Dict[str, str]:
    return {name: service.domain for name, service in SERVICES.items()}