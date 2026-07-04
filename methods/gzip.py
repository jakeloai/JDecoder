import gzip
from typing import Optional

from methods.base import DecodeMethod


class GzipMethod(DecodeMethod):
    name = "gzip"

    def can_decode(self, data: str) -> bool:
        if len(data) < 20:
            return False
        try:
            raw = data.encode("latin-1", errors="replace")
            return raw[:2] == b"\x1f\x8b"
        except Exception:
            return False

    def decode(self, data: str) -> Optional[str]:
        try:
            raw = data.encode("latin-1", errors="replace")
            decompressed = gzip.decompress(raw)
            return decompressed.decode("utf-8", errors="replace")
        except Exception:
            return None

    def encode(self, data: str) -> str:
        compressed = gzip.compress(data.encode("utf-8"))
        return compressed.decode("latin-1", errors="replace")
