import html
import re
from typing import Optional

from methods.base import DecodeMethod


class HTMLMethod(DecodeMethod):
    name = "html"

    _HTML_RE = re.compile(r"&(?:#[0-9]+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*);")
    _MIN_LEN = 4

    def can_decode(self, data: str) -> bool:
        if len(data) < self._MIN_LEN:
            return False
        return bool(self._HTML_RE.search(data))

    def decode(self, data: str) -> Optional[str]:
        try:
            result = html.unescape(data)
            if result != data:
                return result
            return None
        except Exception:
            return None

    def encode(self, data: str) -> str:
        return html.escape(data, quote=True)
