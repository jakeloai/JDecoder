from dataclasses import dataclass
from typing import List, Optional, Tuple
import re


@dataclass
class DecodeStep:
    method: str
    input_data: str
    output_data: str


class DecodeChain:
    def __init__(self, original: str):
        self.original = original
        self.steps: List[DecodeStep] = []
        self.result: Optional[str] = None
        self.readability: float = 0.0
        self.depth: int = 0
        self.duration: float = 0.0
        self.is_plaintext: bool = False
        self.verified: bool = False
        self.verify_error: Optional[str] = None
        self.classification: str = "UNKNOWN"
        self.confidence: float = 0.0

    def add_step(self, method: str, input_data: str, output_data: str):
        self.steps.append(DecodeStep(method, input_data, output_data))
        self.depth += 1

    def get_chain_str(self) -> str:
        return " -> ".join(step.method for step in self.steps) if self.steps else "raw"

    def get_reverse_chain(self) -> str:
        methods = []
        for step in reversed(self.steps):
            m = step.method
            if not m.endswith("_encode") and not m.endswith("_decode"):
                methods.append(f"{m}_encode")
            elif m.endswith("_decode"):
                methods.append(m.replace("_decode", "_encode"))
            else:
                methods.append(m)
        return " -> ".join(methods)

    def clone(self) -> "DecodeChain":
        new = DecodeChain(self.original)
        new.steps = self.steps.copy()
        new.depth = self.depth
        return new

    def verify(self, methods_registry: dict) -> bool:
        """Encode back from result and check if matches original."""
        if not self.steps:
            self.verified = False
            self.verify_error = "No steps to verify"
            return False

        current = self.result
        if current is None:
            self.verified = False
            self.verify_error = "No result to verify"
            return False

        try:
            for step in reversed(self.steps):
                method = methods_registry.get(step.method)
                if method is None:
                    self.verified = False
                    self.verify_error = f"No encoder for {step.method}"
                    return False
                current = method.encode(current)

            original_normalized = self.original.strip()
            current_normalized = current.strip()

            self.verified = (current_normalized == original_normalized)
            if not self.verified:
                self.verify_error = "Encode-back mismatch"
            return self.verified

        except Exception as e:
            self.verified = False
            self.verify_error = str(e)
            return False


class ManualChainParser:
    """Parse manual decode chain DSL.
    e.g. "url,base64" -> [("url", 1), ("base64", 1)]
    e.g. "base64x3,rot13" -> [("base64", 3), ("rot13", 1)]
    """

    _REPEAT_RE = re.compile(r"^(.+?)x(\d+)$")

    @staticmethod
    def parse(chain_str: str) -> List[Tuple[str, int]]:
        if not chain_str:
            return []

        steps = []
        parts = [p.strip() for p in chain_str.split(",") if p.strip()]

        for part in parts:
            match = ManualChainParser._REPEAT_RE.match(part)
            if match:
                method = match.group(1).strip()
                count = int(match.group(2))
                if count < 1:
                    raise ValueError(f"Repeat count must be >= 1, got '{part}'")
                steps.append((method, count))
            else:
                steps.append((part, 1))

        return steps
