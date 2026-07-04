import re
from typing import Optional

from methods.base import DecodeMethod


class UnicodeMethod(DecodeMethod):
    name = "unicode"

    _UNICODE_RE = re.compile(r"\\u[0-9a-fA-F]{4}")
    _HEX_RE = re.compile(r"\\x[0-9a-fA-F]{2}")

    def can_decode(self, data: str) -> bool:
        if len(data) < 6:
            return False
        return bool(self._UNICODE_RE.search(data) or self._HEX_RE.search(data))

    def decode(self, data: str) -> Optional[str]:
        try:
            result = data.encode("utf-8").decode("unicode_escape")
            if result != data:
                return result
            return None
        except Exception:
            return None

    def encode(self, data: str) -> str:
        return data.encode("unicode_escape").decode("ascii")
