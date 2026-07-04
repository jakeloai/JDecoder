# JDecoder

**Multi-path Decoding Engine for Web Application Security Testing**

Author: jakeloai

---

## Overview

JDecoder automatically discovers multi-layer encoding chains used in web applications. Given an encoded string, it exhaustively tries all possible decoding combinations and verifies each result by re-encoding back to the original input.

Designed for bug bounty hunters and web application penetration testers who encounter obfuscated tokens, cookies, API parameters, and serialized data.

---

## Features

- **Auto Explore**: Automatically tries all encoding combinations up to configurable depth
- **Encode-Back Verification**: Every discovered chain is verified by re-encoding the result
- **Manual Chain**: Specify exact decode chain when you know the pattern
- **Batch Processing**: Decode multiple strings from a file
- **Target Pattern Stop**: Stop exploration when result matches your regex
- **Web-Focused Methods**: Only encodings relevant to modern web applications

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Usage

### Auto Explore (Default)

```bash
python jdecoder.py "ZmxhZ3tleGFtcGxlfQ=="
```

### Manual Decode Chain

```bash
python jdecoder.py --chain "url,base64" "ZmxhZ3s..."
python jdecoder.py --chain "base64x3" "Vm0wd2Qy..."
```

### Batch Processing

```bash
python jdecoder.py --file codes.txt
```

### Stop on Pattern Match

```bash
python jdecoder.py --target "flag\{.*\}" "ZmxhZ3s..."
```

### Show All Results (Including Rejected)

```bash
python jdecoder.py --show-all "ZmxhZ3s..."
```

### Disable Colors

```bash
python jdecoder.py --no-color "ZmxhZ3s..."
```

---

## Available Methods

| Method | Aliases | Description |
|--------|---------|-------------|
| `base64` | `b64` | Standard Base64 |
| `base64url` | `b64u` | URL-safe Base64 (RFC 4648) |
| `hex` | - | Hexadecimal encoding |
| `url_decode` | `url`, `uri` | Percent/URL encoding |
| `html` | - | HTML entities |
| `jwt` | - | JSON Web Token decode |
| `unicode` | `utf8` | Unicode escapes (`\uXXXX`, `\xXX`) |
| `gzip` | - | Gzip decompression |
| `zlib` | - | Zlib (deflate with header) |
| `deflate_raw` | `deflate` | Raw deflate (no header) |
| `brotli` | `br` | Brotli decompression |

---

## Classification Levels

Output is color-coded by severity:

| Color | Level | Meaning |
|-------|-------|---------|
| **RED** | CRITICAL | Credentials, secrets, flags, API keys |
| **YELLOW** | HIGH | Structured data with sensitive fields (JWT with weak alg, JSON with role) |
| **LIGHTCYAN** | - | Readable text with security keywords |
| **GREEN** | COMMON | URLs, emails, UUIDs, API endpoints |
| **WHITE** | PLAINTEXT | Other readable text |
| **GREY** | REJECTED | Encode-back verification failed (hidden by default) |

---

## Examples

### JWT Discovery

```bash
$ python jdecoder.py "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

[YELLOW] Chain: jwt
Result: {
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  },
  "signature": "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
Verify: jwt_encode = original OK
Confidence: ████████░░ 85.0%
```

### Multi-Layer Chain

```bash
$ python jdecoder.py --chain "url,base64" "ZmxhZ3s..."

[HIGH] Chain: url_decode -> base64
Result: {"role":"admin","secret":"sk_live_abc123"}
Verify: base64_encode -> url_encode = original OK
Confidence: ████████░░ 90.0%
```

---

## Options

| Option | Description |
|--------|-------------|
| `--chain, -c` | Manual decode chain (e.g., `base64,url`) |
| `--file, -f` | File with encoded strings (one per line) |
| `--target, -t` | Regex pattern to stop exploration |
| `--max-depth` | Maximum decode depth (default: 8) |
| `--max-paths` | Maximum paths to explore (default: 200) |
| `--list-methods` | Show available decoding methods |
| `--show-all` | Include rejected paths in output |
| `--no-color` | Disable colored output |
| `--no-verify` | Skip encode-back verification (not recommended) |

---

## License

MIT License - Use at your own risk for authorized security testing only.
