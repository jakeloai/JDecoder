# JLFDecoder

> Designed by **jakelo.ai** · Coded with AI assistance

You give it an encoded string. It tries every possible combination of decoding methods, then checks if re-encoding the result gives you back the original string. The ones that pass get shown to you.

---

## What it does

You have a token, cookie, or API parameter that looks encoded. You don't know which encoding was used, or if multiple layers were stacked. JLFDecoder tries every possible chain of decoders (up to a depth you set) and verifies each result by re-encoding it back to the original input.

If the round-trip works, the chain is probably correct.

---

## Installation

```bash
pip install -r requirements.txt
```

---

## How to use

**Auto-explore all possible decoding chains:**

```bash
python jlfdecoder.py "ZmxhZ3tleGFtcGxlfQ=="
```

**Specify a known chain manually:**

```bash
python jlfdecoder.py --chain "url,base64" "ZmxhZ3s..."
python jlfdecoder.py --chain "base64x3" "Vm0wd2Qy..."
```

**Process multiple strings from a file:**

```bash
python jlfdecoder.py --file codes.txt
```

**Stop when result matches a pattern:**

```bash
python jlfdecoder.py --target "flag\{.*\}" "ZmxhZ3s..."
```

**Show all results including failed verifications:**

```bash
python jlfdecoder.py --show-all "ZmxhZ3s..."
```

**Disable colored output:**

```bash
python jlfdecoder.py --no-color "ZmxhZ3s..."
```

---

## Available methods

| Method | Aliases | What it does |
|---|---|---|
| `base64` | `b64` | Standard Base64 decode |
| `base64url` | `b64u` | URL-safe Base64 (RFC 4648) |
| `hex` | — | Hex string to bytes |
| `url_decode` | `url`, `uri` | Percent-decoding |
| `html` | — | HTML entity decoding |
| `jwt` | — | JWT payload extraction |
| `unicode` | `utf8` | `\uXXXX` and `\xXX` escape decoding |
| `gzip` | — | Gzip decompression |
| `zlib` | — | Zlib decompression |
| `deflate_raw` | `deflate` | Raw deflate (no header) |
| `brotli` | `br` | Brotli decompression |

---

## How it decides what to show

Each result is checked by re-encoding the decoded output back through the same chain. If it matches the original input, it passes. If not, it gets rejected (hidden by default).

Results are also color-coded by what they look like:

| Color | What it means |
|---|---|
| **Red** | Looks like credentials, secrets, API keys, or flags |
| **Yellow** | Structured data with sensitive fields (JWT with weak algorithm, JSON with role fields) |
| **Light cyan** | Readable text containing security-related keywords |
| **Green** | URLs, emails, UUIDs, API endpoints |
| **White** | Other readable text |
| **Grey** | Failed verification (hidden unless `--show-all`) |

---

## Examples

**JWT discovery:**

```bash
$ python jlfdecoder.py "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

[YELLOW] Chain: jwt
Result: {
  "header": {"alg": "HS256", "typ": "JWT"},
  "payload": {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
}
Verify: jwt_encode = original OK
Confidence: 85.0%
```

**Multi-layer chain:**

```bash
$ python jlfdecoder.py --chain "url,base64" "ZmxhZ3s..."

[HIGH] Chain: url_decode -> base64
Result: {"role":"admin","secret":"sk_live_abc123"}
Verify: base64_encode -> url_encode = original OK
Confidence: 90.0%
```

---

## Options

| Option | Description |
|---|---|
| `--chain, -c` | Manual decode chain (e.g., `base64,url`) |
| `--file, -f` | File with encoded strings (one per line) |
| `--target, -t` | Regex pattern to stop exploration when matched |
| `--max-depth` | Maximum decode depth (default: 8) |
| `--max-paths` | Maximum paths to explore (default: 200) |
| `--list-methods` | Show available decoding methods |
| `--show-all` | Include rejected paths in output |
| `--no-color` | Disable colored output |
| `--no-verify` | Skip encode-back verification (not recommended) |

---

## License

MIT © jakelo.ai
