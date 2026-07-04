import brotli
from typing import Optional

from methods.base import DecodeMethod


class BrotliMethod(DecodeMethod):
    name = "brotli"

    def can_decode(self, data: str) -> bool:
        if len(data) < 10:
            return False
        return True

    def decode(self, data: str) -> Optional[str]:
        try:
            raw = data.encode("latin-1", errors="replace")
            decompressed = brotli.decompress(raw)
            return decompressed.decode("utf-8", errors="replace")
        except Exception:
            return None

    def encode(self, data: str) -> str:
        compressed = brotli.compress(data.encode("utf-8"))
        return compressed.decode("latin-1", errors="replace")
