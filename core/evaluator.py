import json
import re
from typing import Tuple


class Evaluator:
    """Evaluate decoded results for bug bounty web application testing."""

    CRITICAL_PATTERNS = {
        "flag": re.compile(r"flag\{[^}]+\}", re.IGNORECASE),
        "secret": re.compile(r"(?i)(secret|api[_-]?key|private[_-]?key|access[_-]?token)\s*[:=]\s*[\'\"]?[\w\-]+"),
        "password": re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*[\'\"]?[^\'\"\s]+"),
        "token": re.compile(r"(?i)(bearer\s+)?[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+"),
        "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "private_key": re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    }

    HIGH_PATTERNS = {
        "jwt_weak": re.compile(r"\"alg\"\s*:\s*\"(none|HS256|HS384)\""),
        "json_role": re.compile(r"(?i)\"role\"\s*:\s*\"[^\"]*(admin|root|super|moderator)[^\"]*\""),
        "json_sensitive": re.compile(r"(?i)\"(email|phone|ssn|credit[_-]?card|password|secret)\"\s*:\s*\"[^\"]+\""),
        "internal_ip": re.compile(r"(?i)(10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)"),
    }

    COMMON_PATTERNS = {
        "email": re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"),
        "url": re.compile(r"https?://[^\s\"<>]+"),
        "uuid": re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
        "api_endpoint": re.compile(r"/api/v\d+/[a-zA-Z0-9_-]+"),
    }

    KEYWORDS = [
        "admin", "root", "system", "config", "debug", "test",
        "dev", "staging", "prod", "internal", "backup", "secret",
        "key", "token", "auth", "session", "cookie", "password",
        "credential", "private", "confidential", "restricted",
    ]

    def evaluate(self, data: str) -> Tuple[float, bool, str, float]:
        """Evaluate data and return (readability, is_plaintext, classification, confidence)."""
        if not data:
            return 0.0, False, "UNKNOWN", 0.0

        for name, pattern in self.CRITICAL_PATTERNS.items():
            if pattern.search(data):
                return 0.9, True, "CRITICAL", 0.95

        for name, pattern in self.HIGH_PATTERNS.items():
            if pattern.search(data):
                return 0.8, True, "HIGH", 0.85

        structured_score = self._structured_score(data)
        if structured_score > 0:
            return 0.7, True, "HIGH", structured_score

        readability = self._readability(data)
        common_found = any(p.search(data) for p in self.COMMON_PATTERNS.values())
        keyword_found = any(kw in data.lower() for kw in self.KEYWORDS)

        if readability > 0.7 and (common_found or keyword_found):
            return readability, True, "LIGHTCYAN", 0.75
        elif readability > 0.7:
            return readability, True, "WHITE", 0.7
        elif readability > 0.5:
            return readability, True, "GREEN", 0.6 if common_found else 0.5
        elif common_found:
            return readability, False, "GREEN", 0.4

        return readability, False, "UNKNOWN", 0.0

    def _readability(self, data: str) -> float:
        if not data:
            return 0.0

        printable = sum(1 for c in data if c.isprintable() or c.isspace())
        printable_ratio = printable / len(data)

        word_chars = sum(1 for c in data if c.isalnum() or c in " ._-:/@{}[]()")
        word_ratio = word_chars / len(data)

        space_ratio = data.count(" ") / max(len(data), 1)

        score = (printable_ratio * 0.4) + (word_ratio * 0.4) + (min(space_ratio * 5, 0.2) * 0.2)
        return min(score, 1.0)

    def _structured_score(self, data: str) -> float:
        try:
            parsed = json.loads(data)
            sensitive_keys = ["role", "admin", "secret", "password", "token", "key", "auth"]
            if isinstance(parsed, dict):
                for k in parsed.keys():
                    if any(s in k.lower() for s in sensitive_keys):
                        return 0.9
            return 0.7
        except (json.JSONDecodeError, ValueError):
            pass

        if data.count(".") == 2 and all(len(p) > 0 for p in data.split(".")):
            parts = data.split(".")
            if all(re.match(r'^[A-Za-z0-9_-]+$', p) for p in parts[:2]):
                return 0.75

        if data.strip().startswith("<?xml") or (data.strip().startswith("<") and ">" in data):
            return 0.6

        return 0.0

    def check_target(self, data: str, target_regex: re.Pattern) -> bool:
        return bool(target_regex.search(data))
