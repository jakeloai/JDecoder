import zlib
from typing import Optional

from methods.base import DecodeMethod


class DeflateRawMethod(DecodeMethod):
    name = "deflate_raw"

    def can_decode(self, data: str) -> bool:
        if len(data) < 10:
            return False
        return True

    def decode(self, data: str) -> Optional[str]:
        try:
            raw = data.encode("latin-1", errors="replace")
            decompressed = zlib.decompress(raw, -15)
            return decompressed.decode("utf-8", errors="replace")
        except Exception:
            return None

    def encode(self, data: str) -> str:
        compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
        compressed = compressor.compress(data.encode("utf-8")) + compressor.flush()
        return compressed.decode("latin-1", errors="replace")
