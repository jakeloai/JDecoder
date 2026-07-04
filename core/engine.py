import time
from collections import deque
from typing import List, Optional

from core.chain import DecodeChain, ManualChainParser
from core.evaluator import Evaluator
from methods import METHODS, resolve_method


class DecodeEngine:
    def __init__(self, max_depth: int = 8, max_paths: int = 200,
                 target_regex=None):
        self.max_depth = max_depth
        self.max_paths = max_paths
        self.target_regex = target_regex
        self.evaluator = Evaluator()
        self.methods = METHODS
        self.results: List[DecodeChain] = []

    def explore(self, data: str) -> List[DecodeChain]:
        self.results = []
        queue = deque([(DecodeChain(data), data, 0)])
        paths_explored = 0
        start_time = time.time()

        while queue and paths_explored < self.max_paths:
            chain, current, depth = queue.popleft()
            paths_explored += 1

            readability, is_plain, classification, confidence = self.evaluator.evaluate(current)

            if depth == 0:
                is_plain = False
                classification = "UNKNOWN"
                confidence = 0.0

            result_chain = chain.clone()
            result_chain.result = current
            result_chain.readability = readability
            result_chain.depth = depth
            result_chain.duration = time.time() - start_time
            result_chain.is_plaintext = is_plain
            result_chain.classification = classification
            result_chain.confidence = confidence

            if depth > 0:
                result_chain.verify(self.methods)
            else:
                result_chain.verified = False

            self.results.append(result_chain)

            if self.target_regex and depth > 0:
                if self.evaluator.check_target(current, self.target_regex):
                    break

            if depth >= self.max_depth:
                continue

            for name, method in self.methods.items():
                if not method.can_decode(current):
                    continue
                try:
                    decoded = method.decode(current)
                    if decoded and decoded != current and len(decoded) > 0:
                        new_chain = chain.clone()
                        new_chain.add_step(name, current, decoded)
                        queue.append((new_chain, decoded, depth + 1))
                except Exception:
                    continue

        priority = {"CRITICAL": 5, "HIGH": 4, "LIGHTCYAN": 3, "GREEN": 2, "WHITE": 1, "UNKNOWN": 0}
        self.results.sort(
            key=lambda x: (
                x.verified,
                priority.get(x.classification, 0),
                x.confidence,
                x.readability,
            ),
            reverse=True,
        )
        return self.results

    def run_manual_chain(self, data: str, chain_str: str) -> DecodeChain:
        chain = DecodeChain(data)
        current = data
        steps = ManualChainParser.parse(chain_str)

        for method_alias, count in steps:
            method_key = resolve_method(method_alias)
            method = self.methods[method_key]

            for _ in range(count):
                try:
                    decoded = method.decode(current)
                    if decoded is None or decoded == current:
                        raise ValueError(
                            f"Method '{method_alias}' produced no change on: '{current[:50]}...'"
                        )
                except Exception as e:
                    if isinstance(e, ValueError):
                        raise
                    raise ValueError(f"Method '{method_alias}' failed: {e}")

                chain.add_step(method_key, current, decoded)
                current = decoded

        chain.result = current
        readability, is_plain, classification, confidence = self.evaluator.evaluate(current)
        chain.readability = readability
        chain.is_plaintext = is_plain
        chain.classification = classification
        chain.confidence = confidence
        chain.depth = len(chain.steps)
        chain.verify(self.methods)
        return chain

    def get_verified_paths(self) -> List[DecodeChain]:
        return [r for r in self.results if r.verified]

    def get_rejected_paths(self) -> List[DecodeChain]:
        return [r for r in self.results if not r.verified and r.depth > 0]

    def get_target_matches(self) -> List[DecodeChain]:
        if not self.target_regex:
            return []
        return [
            r for r in self.results
            if r.verified and self.evaluator.check_target(r.result or "", self.target_regex)
        ]
