import urllib.parse
import re
from typing import Optional

from methods.base import DecodeMethod


class URLMethod(DecodeMethod):
    name = "url_decode"

    _URL_RE = re.compile(r"%[0-9a-fA-F]{2}|\+")
    _MIN_LEN = 3

    def can_decode(self, data: str) -> bool:
        if len(data) < self._MIN_LEN:
            return False
        return bool(self._URL_RE.search(data))

    def decode(self, data: str) -> Optional[str]:
        try:
            # Handle + as space (application/x-www-form-urlencoded)
            result = urllib.parse.unquote_plus(data)
            if result != data:
                return result
            # Try standard unquote if plus didn't change
            result = urllib.parse.unquote(data)
            if result != data:
                return result
            return None
        except Exception:
            return None

    def encode(self, data: str) -> str:
        # Use standard percent encoding
        return urllib.parse.quote(data, safe="")
