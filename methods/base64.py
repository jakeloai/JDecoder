import base64
import re
from typing import Optional

from methods.base import DecodeMethod


class Base64Method(DecodeMethod):
    name = "base64"

    _B64_RE = re.compile(r"^[A-Za-z0-9+/]*={0,2}$")
    _MIN_LEN = 4

    def can_decode(self, data: str) -> bool:
        if len(data) < self._MIN_LEN:
            return False
        # Remove whitespace for check
        cleaned = "".join(data.split())
        if len(cleaned) % 4 != 0:
            return False
        if not self._B64_RE.match(cleaned):
            return False
        return True

    def decode(self, data: str) -> Optional[str]:
        cleaned = "".join(data.split())
        try:
            decoded = base64.b64decode(cleaned, validate=True)
            return decoded.decode("utf-8", errors="replace")
        except Exception:
            return None

    def encode(self, data: str) -> str:
        return base64.b64encode(data.encode("utf-8")).decode("ascii")
