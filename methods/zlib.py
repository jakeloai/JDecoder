import zlib
from typing import Optional

from methods.base import DecodeMethod


class ZlibMethod(DecodeMethod):
    name = "zlib"

    def can_decode(self, data: str) -> bool:
        if len(data) < 10:
            return False
        try:
            raw = data.encode("latin-1", errors="replace")
            cmf = raw[0]
            cm = cmf & 0x0f
            return cm == 8
        except Exception:
            return False

    def decode(self, data: str) -> Optional[str]:
        try:
            raw = data.encode("latin-1", errors="replace")
            decompressed = zlib.decompress(raw)
            return decompressed.decode("utf-8", errors="replace")
        except Exception:
            return None

    def encode(self, data: str) -> str:
        compressed = zlib.compress(data.encode("utf-8"))
        return compressed.decode("latin-1", errors="replace")
