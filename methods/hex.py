import re
from typing import Optional

from methods.base import DecodeMethod


class HexMethod(DecodeMethod):
    name = "hex"

    _HEX_RE = re.compile(r"^(0x)?[0-9a-fA-F\s]+$")
    _MIN_LEN = 2

    def can_decode(self, data: str) -> bool:
        if len(data.strip()) < self._MIN_LEN:
            return False
        cleaned = data.strip().replace("0x", "").replace(" ", "").replace("\n", "").replace("\t", "")
        if len(cleaned) % 2 != 0:
            return False
        if not all(c in "0123456789abcdefABCDEF" for c in cleaned):
            return False
        return True

    def decode(self, data: str) -> Optional[str]:
        cleaned = data.strip().replace("0x", "").replace(" ", "").replace("\n", "").replace("\t", "")
        try:
            decoded = bytes.fromhex(cleaned)
            return decoded.decode("utf-8", errors="replace")
        except Exception:
            return None

    def encode(self, data: str) -> str:
        return data.encode("utf-8").hex()
