import base64
import re
from typing import Optional

from methods.base import DecodeMethod


class Base64URLMethod(DecodeMethod):
    name = "base64url"

    _B64URL_RE = re.compile(r"^[A-Za-z0-9_-]*$")
    _MIN_LEN = 4

    def can_decode(self, data: str) -> bool:
        if len(data) < self._MIN_LEN:
            return False
        cleaned = "".join(data.split())
        if not self._B64URL_RE.match(cleaned):
            return False
        # Base64URL typically has no padding, but some implementations add it
        # Check length is reasonable (not too short for base64)
        return True

    def decode(self, data: str) -> Optional[str]:
        cleaned = "".join(data.split())
        try:
            # Add padding if needed
            padding_needed = 4 - (len(cleaned) % 4)
            if padding_needed != 4:
                cleaned += "=" * padding_needed
            decoded = base64.urlsafe_b64decode(cleaned)
            return decoded.decode("utf-8", errors="replace")
        except Exception:
            return None

    def encode(self, data: str) -> str:
        # Base64URL without padding (standard for JWT)
        encoded = base64.urlsafe_b64encode(data.encode("utf-8")).decode("ascii")
        return encoded.rstrip("=")
