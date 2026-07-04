from .base import DecodeMethod
from .base64 import Base64Method
from .base64url import Base64URLMethod
from .brotli import BrotliMethod
from .deflate import DeflateRawMethod
from .gzip import GzipMethod
from .hex import HexMethod
from .html import HTMLMethod
from .jwt import JWTMethod
from .unicode import UnicodeMethod
from .url import URLMethod
from .zlib import ZlibMethod

__all__ = [
    "DecodeMethod",
    "Base64Method",
    "Base64URLMethod",
    "BrotliMethod",
    "DeflateRawMethod",
    "GzipMethod",
    "HexMethod",
    "HTMLMethod",
    "JWTMethod",
    "UnicodeMethod",
    "URLMethod",
    "ZlibMethod",
    "METHODS",
    "METHOD_ALIASES",
    "resolve_method",
    "get_encoder",
]

METHODS = {
    "base64": Base64Method(),
    "base64url": Base64URLMethod(),
    "hex": HexMethod(),
    "url_decode": URLMethod(),
    "html": HTMLMethod(),
    "jwt": JWTMethod(),
    "unicode": UnicodeMethod(),
    "gzip": GzipMethod(),
    "zlib": ZlibMethod(),
    "deflate_raw": DeflateRawMethod(),
    "brotli": BrotliMethod(),
}

METHOD_ALIASES = {
    "b64": "base64",
    "base64": "base64",
    "b64u": "base64url",
    "base64url": "base64url",
    "hex": "hex",
    "url": "url_decode",
    "uri": "url_decode",
    "url_decode": "url_decode",
    "html": "html",
    "jwt": "jwt",
    "unicode": "unicode",
    "utf8": "unicode",
    "gzip": "gzip",
    "zlib": "zlib",
    "deflate": "deflate_raw",
    "deflate_raw": "deflate_raw",
    "brotli": "brotli",
    "br": "brotli",
}


def resolve_method(name: str) -> str:
    """Resolve user-friendly method name to internal METHODS key."""
    key = name.lower().strip()
    if key in METHODS:
        return key
    if key in METHOD_ALIASES:
        return METHOD_ALIASES[key]
    raise ValueError(f"Unknown method '{name}'. Use --list-methods to see available methods.")


def get_encoder(method_key: str) -> DecodeMethod:
    """Get the encode method for reverse verification."""
    return METHODS[method_key]
