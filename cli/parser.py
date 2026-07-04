import argparse
import re


def create_parser():
    parser = argparse.ArgumentParser(
        description="JDECODER - Multi-path Decoding Engine for Web Application Security Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  Auto explore (default):
    python jdecoder.py "ZmxhZ3tleGFtcGxlfQ=="

  Manual decode chain:
    python jdecoder.py --chain "url,base64" "ZmxhZ3s..."

  Repeat decode:
    python jdecoder.py --chain "base64x3" "Vm0wd2Qy..."

  Stop on pattern match:
    python jdecoder.py --target "flag\\{.*\\}" "ZmxhZ3s..."

  Batch processing from file:
    python jdecoder.py --file codes.txt

  List available methods:
    python jdecoder.py --list-methods

  Show rejected paths too:
    python jdecoder.py --show-all "ZmxhZ3s..."

  Disable colors:
    python jdecoder.py --no-color "ZmxhZ3s..."

METHOD PRIORITY (auto explore order):
  url_decode, base64, base64url, hex, html, jwt, unicode,
  gzip, zlib, deflate_raw, brotli

CLASSIFICATION LEVELS:
  [RED]     CRITICAL    - Credentials, secrets, flags found
  [YELLOW]  HIGH        - Structured data with sensitive fields
  [LIGHTCYAN]           - Readable text with security keywords
  [GREEN]   COMMON      - URLs, emails, UUIDs, API endpoints
  [WHITE]   PLAINTEXT   - Other readable text
  [GREY]    REJECTED    - Encode-back verification failed
        """,
    )

    parser.add_argument(
        "data",
        nargs="?",
        help="Encoded data string to decode"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        metavar="FILE",
        help="File containing encoded strings (one per line)"
    )
    parser.add_argument(
        "--chain", "-c",
        type=str,
        metavar='"method1,method2x3,..."',
        help='Manual decode chain. Comma-separated, "xN" for repeat (e.g. base64x3,url)'
    )
    parser.add_argument(
        "--target", "-t",
        type=str,
        metavar="REGEX",
        help="Stop exploring when result matches regex pattern"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=8,
        help="Maximum decoding depth (default: 8)"
    )
    parser.add_argument(
        "--max-paths",
        type=int,
        default=200,
        help="Maximum paths to explore (default: 200)"
    )
    parser.add_argument(
        "--list-methods",
        action="store_true",
        help="List available decoding methods"
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show rejected paths too (default: hide verified-failed)"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip encode-back verification (not recommended)"
    )

    return parser


def compile_target(target_str: str):
    try:
        return re.compile(target_str)
    except re.error as e:
        raise ValueError(f"Invalid target regex: {e}")
