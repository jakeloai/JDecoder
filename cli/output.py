import sys
from typing import List

from core.chain import DecodeChain


class Colors:
    RED = "\033[1;31m"
    YELLOW = "\033[1;33m"
    LIGHTCYAN = "\033[1;36m"
    BLUE = "\033[1;34m"
    GREEN = "\033[1;32m"
    WHITE = "\033[1;37m"
    GREY = "\033[0;37m"
    DIM = "\033[2m"
    RESET = "\033[0m"


class OutputFormatter:
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors

    def _color(self, text: str, color: str) -> str:
        if not self.use_colors:
            return text
        return f"{color}{text}{Colors.RESET}"

    def _get_class_color(self, classification: str) -> str:
        mapping = {
            "CRITICAL": Colors.RED,
            "HIGH": Colors.YELLOW,
            "LIGHTCYAN": Colors.LIGHTCYAN,
            "BLUE": Colors.BLUE,
            "GREEN": Colors.GREEN,
            "WHITE": Colors.WHITE,
            "UNKNOWN": Colors.GREY,
        }
        return mapping.get(classification, Colors.WHITE)

    def print_header(self, total_paths: int, verified_count: int = 0):
        print("=" * 70)
        print("JDECODER - WEB APPLICATION DECODE RESULTS")
        print("=" * 70)
        print(f"Total paths explored: {total_paths}")
        if verified_count > 0:
            print(f"Verified paths: {verified_count}")
        print()
        print("Review each path and pick the one that makes sense.")
        print("Each path shows the FULL decode chain so you can reverse it.")
        print()

    def print_methods(self, methods: dict):
        print("Available decoding methods:")
        print("-" * 40)
        for name, method in sorted(methods.items()):
            print(f"  - {name:<20} ({method.__class__.__name__})")
        print()

    def print_chain(self, chain: DecodeChain, index: int, show_rejected: bool = False):
        if not chain.verified and not show_rejected and chain.depth > 0:
            return

        is_rejected = not chain.verified and chain.depth > 0

        if is_rejected:
            tag = "[REJECTED]"
            color = Colors.GREY
        else:
            tag = f"[{chain.classification}]"
            color = self._get_class_color(chain.classification)

        print("-" * 70)
        print(f"PATH #{index:>3} {self._color(tag, color)}")
        print("-" * 70)

        original_display = chain.original[:80] + "..." if len(chain.original) > 80 else chain.original
        result_display = (chain.result or "")[:80] + "..." if len(chain.result or "") > 80 else (chain.result or "")

        print(f"Original:  {original_display}")
        print(f"Chain:     {chain.get_chain_str()}")
        print(f"Result:    {result_display}")

        if chain.verified:
            print(f"Verify:    {chain.get_reverse_chain()} = original OK")
        elif is_rejected:
            print(f"Verify:    FAILED - {chain.verify_error or 'encode-back mismatch'}")

        bar_len = 10
        filled = int(chain.confidence * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"Confidence: {self._color(bar, color)} {chain.confidence*100:.1f}%")

        if chain.readability > 0:
            print(f"Readability: {chain.readability*100:.2f}%")

        print(f"Depth:     {chain.depth}")
        print()

    def print_results(self, results: List[DecodeChain], show_all: bool = False):
        verified = [r for r in results if r.verified]
        rejected = [r for r in results if not r.verified and r.depth > 0]

        idx = 1
        for chain in verified:
            self.print_chain(chain, idx, show_all)
            idx += 1

        if show_all and rejected:
            print("=" * 70)
            print(self._color("REJECTED PATHS (encode-back mismatch)", Colors.GREY))
            print("=" * 70)
            print()

            for chain in rejected:
                self.print_chain(chain, idx, True)
                idx += 1

    def print_footer(self, verified_count: int = 0, rejected_count: int = 0):
        print("=" * 70)
        print("END OF OUTPUT")
        print("=" * 70)
        if verified_count > 0:
            print(f"{verified_count} verified path(s) found.")
        if rejected_count > 0:
            print(f"{rejected_count} rejected path(s) hidden. Use --show-all to see.")
        print()

    def print_manual_result(self, chain: DecodeChain):
        status = chain.classification if chain.verified else "REJECTED"
        color = self._get_class_color(status) if chain.verified else Colors.GREY

        print("=" * 70)
        print(self._color(f"MANUAL CHAIN RESULT [{status}]", color))
        print("=" * 70)
        print(f"Chain:     {chain.get_chain_str()}")
        print(f"Result:    {chain.result}")
        print(f"Depth:     {chain.depth}")

        if chain.verified:
            print(f"Verify:    {chain.get_reverse_chain()} = original OK")
        else:
            print(f"Verify:    FAILED - {chain.verify_error or 'encode-back mismatch'}")

        print(f"Confidence: {chain.confidence*100:.1f}%")
        print("=" * 70)
        print()

    def print_error(self, message: str):
        print(self._color(f"[ERROR] {message}", Colors.RED), file=sys.stderr)

    def print_success(self, message: str):
        print(self._color(f"[OK] {message}", Colors.GREEN))
