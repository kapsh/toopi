"""Actual work with pastebins."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Type
from urllib.parse import urljoin

from . import utils

log = logging.getLogger(__name__)


@dataclass
class PasteResult:  # TODO enum?
    """What can be returned after sending text."""

    nice_url: str
    raw_url: str


class PasteEngine:
    """How to work with pastebin engine."""

    default_expiry: str = None
    expiries = None

    def __init__(self, domain: str, api_domain: Optional[str] = None):
        self.domain = domain
        self.api_domain = api_domain

    def post(self, text, title, language, expiry) -> PasteResult:
        """Send text to this pastebin."""


class Pinnwand(PasteEngine):
    """Pinnwand engine.

    https://github.com/supakeen/pinnwand
    """

    default_expiry = "1week"
    expiries = ["1day", "1week"]

    def post(self, text, title, language, expiry) -> PasteResult:
        with utils.strict_http_session() as session:
            response = session.post(
                urljoin(self.domain, "/json/new"),
                data={"code": text, "lexer": language, "expiry": expiry},
            )
        paste_id = response.json()["paste_id"]
        return PasteResult(
            urljoin(self.domain, f"/show/{paste_id}"),
            urljoin(self.domain, f"/raw/{paste_id}"),
        )


class DpasteCom(PasteEngine):
    """dpaste.com engine (unnamed?)."""

    default_expiry = "30"
    expiries = "[1..365] (in days)"

    def post(self, text, title, language, expiry) -> PasteResult:
        with utils.strict_http_session() as session:
            response = session.post(
                urljoin(self.domain, "/api/v2/"),
                data={
                    "content": text,
                    "title": title,
                    "syntax": language,
                    "expiry_days": expiry,
                },
            )
        return PasteResult(
            response.headers["location"], response.headers["location"] + ".txt"
        )


class PasteGg(PasteEngine):
    """paste.gg engine.

    https://github.com/jkcclemens/paste/
    """

    default_expiry = "7"
    expiries = "[1..365] (in days)"

    def post(self, text, title, language, expiry) -> PasteResult:
        # TODO only anonymous for now

        keep_until = datetime.now(timezone.utc) + timedelta(days=int(expiry))
        with utils.strict_http_session() as session:
            response = session.post(
                urljoin(self.api_domain, "/v1/pastes/"),
                headers={"Content-Type": "application/json"},
                json={
                    "expires": keep_until.isoformat(timespec="seconds"),
                    "files": [
                        {"name": title, "content": {"format": "text", "value": text}}
                    ],
                },
            )
        result = response.json()["result"]
        paste_id = result["id"]
        first_file_id = result["files"][0]["id"]
        return PasteResult(
            urljoin(self.domain, f"/p/anonymous/{paste_id}"),
            urljoin(self.domain, f"/p/anonymous/{paste_id}/files/{first_file_id}/raw"),
        )


@dataclass
class ServiceInfo:
    """Information about site."""

    domain: str
    engine: Type[PasteEngine]
    api_domain: Optional[str] = None


SERVICES = {
    "bpaste": ServiceInfo("https://bpaste.net/", Pinnwand),
    "dpaste": ServiceInfo("http://dpaste.com", DpasteCom),
    "pastegg": ServiceInfo(
        "https://paste.gg/", PasteGg, api_domain="https://api.paste.gg/"
    ),
}

DEFAULT_SERVICE = "bpaste"


def paste_engine(service_code: str) -> PasteEngine:
    """Create paste engine by known code."""
    service = SERVICES[service_code]
    return service.engine(service.domain, service.api_domain)  # TODO simpler init


def services_info() -> Dict[str, str]:
    """Return name and url for known paste services."""
    return {name: service.domain for name, service in SERVICES.items()}
