#!/usr/bin/env python3
"""
JLFDecoder - Multi-path Decoding Engine for Web Application Security Testing
Author: jakeloai

A focused decoding tool for bug bounty hunters and web application security testers.
Automatically discovers multi-layer encoding chains with encode-back verification.
"""

import sys

from cli.output import OutputFormatter
from cli.parser import create_parser, compile_target
from core.engine import DecodeEngine
from methods import METHODS


def process_single(data, args, formatter):
    engine = DecodeEngine(
        max_depth=args.max_depth,
        max_paths=args.max_paths,
        target_regex=compile_target(args.target) if args.target else None,
    )

    if args.chain:
        try:
            chain = engine.run_manual_chain(data, args.chain)
            formatter.print_manual_result(chain)
            if not chain.verified and not args.no_verify:
                formatter.print_error("Chain failed verification. Use --no-verify to bypass.")
                sys.exit(1)
        except ValueError as e:
            formatter.print_error(f"Manual chain failed: {e}")
            sys.exit(1)
        return

    engine.explore(data)

    verified = engine.get_verified_paths()
    rejected = engine.get_rejected_paths()

    formatter.print_header(len(engine.results), len(verified))
    formatter.print_results(engine.results, args.show_all)
    formatter.print_footer(len(verified), len(rejected))


def process_file(filepath, args, formatter):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        formatter.print_error(f"File not found: {filepath}")
        sys.exit(1)
    except PermissionError:
        formatter.print_error(f"Permission denied: {filepath}")
        sys.exit(1)

    print(f"Processing {len(lines)} encoded strings from {filepath}")
    print("=" * 70)

    for i, line in enumerate(lines, 1):
        display = line[:60] + "..." if len(line) > 60 else line
        print(f"\n--- Input #{i}: {display} ---")
        process_single(line, args, formatter)


def main():
    parser = create_parser()
    args = parser.parse_args()

    formatter = OutputFormatter(use_colors=not args.no_color)

    if args.list_methods:
        formatter.print_methods(METHODS)
        return

    if not args.data and not args.file:
        parser.print_help()
        sys.exit(1)

    if args.file:
        process_file(args.file, args, formatter)
    else:
        process_single(args.data, args, formatter)


if __name__ == "__main__":
    main()
