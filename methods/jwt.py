import base64
import json
import re
from typing import Optional

from methods.base import DecodeMethod


class JWTMethod(DecodeMethod):
    name = "jwt"

    _JWT_RE = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*$")
    _MIN_LEN = 10

    def can_decode(self, data: str) -> bool:
        if len(data) < self._MIN_LEN:
            return False
        return bool(self._JWT_RE.match(data.strip()))

    def decode(self, data: str) -> Optional[str]:
        cleaned = data.strip()
        parts = cleaned.split(".")
        if len(parts) != 3:
            return None

        try:
            header_b64 = self._add_padding(parts[0])
            payload_b64 = self._add_padding(parts[1])

            header = base64.urlsafe_b64decode(header_b64).decode("utf-8", errors="replace")
            payload = base64.urlsafe_b64decode(payload_b64).decode("utf-8", errors="replace")

            header_json = json.loads(header)
            payload_json = json.loads(payload)

            result = {
                "header": header_json,
                "payload": payload_json,
                "signature": parts[2]
            }
            return json.dumps(result, indent=2)
        except Exception:
            return None

    def encode(self, data: str) -> str:
        try:
            parsed = json.loads(data)
            header = json.dumps(parsed["header"], separators=(",", ":"))
            payload = json.dumps(parsed["payload"], separators=(",", ":"))

            header_b64 = base64.urlsafe_b64encode(header.encode()).decode().rstrip("=")
            payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
            sig = parsed.get("signature", "")

            return f"{header_b64}.{payload_b64}.{sig}"
        except Exception:
            encoded = base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")
            return f"{encoded}."

    @staticmethod
    def _add_padding(data: str) -> str:
        padding_needed = 4 - (len(data) % 4)
        if padding_needed != 4:
            data += "=" * padding_needed
        return data
