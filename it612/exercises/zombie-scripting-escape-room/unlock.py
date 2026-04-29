#!/usr/bin/env python3
"""
Override gate for the server-room lockdown.

Usage:
    python3 unlock.py <4-digit-code>

Exit codes:
    0  ESCAPED        - code accepted, lockdown released
    1  STILL TRAPPED  - wrong code; door holds
    2  USAGE          - bad input (missing arg, non-numeric, wrong length)

Design note (read this only after solving):
    The four-digit code is never stored anywhere in this file. The gate
    compares sha256(K + candidate) against a precomputed digest, where K
    is derived at runtime from a seed string -- so the salt itself never
    appears as a literal in the source either. On a correct match an
    embedded ciphertext is XOR-decrypted with sha256(candidate) and
    printed. A wrong code yields gibberish, so the program just prints
    STILL TRAPPED and returns 1 with no partial leakage.
"""
from __future__ import annotations

import hashlib
import sys

# Derived at import time. The literal value never appears in source.
_K = hashlib.blake2b(b"outbreak-protocol/lockdown-override/v1",
                     digest_size=16).digest()

# sha256(_K || correct_code).hexdigest() -- precomputed at build time.
_H = "69b5026ea49959ab2d95e8984da7ced98a9a34532eb6bd753d2b27477cd50595"

# Ciphertext of the success banner; XOR-encoded with sha256(correct_code).
_C = bytes.fromhex(
    "f3a5f5300feb4c0915034f74993a8dbd671ae29b4055867407330d44653d5e64"
    "d59dd21e28c0285b5d420a5a9c3a9bef6f0aa78b120cd1264d765a001e495125"
    "bcb5d91f2bcf6147554b014fcf3790a36a0da99b724397671e3107523827323f"
    "98d6e5142dd86d5b185c0054827f8caa6d0bf5de0f3cb17912670c49386d737f"
    "d59ed3037fca694c5541011b862cdfbc660bf39b4559927f59673c482e3d7a64"
    "c492d3512dcb7c5b5d4f1b48c155"
)


def _usage(stream=sys.stderr) -> None:
    stream.write("usage: unlock.py <4-digit-code>\n")
    stream.write("       code must be exactly 4 numeric digits, e.g. 0042\n")


def _validate(code: str) -> bool:
    return len(code) == 4 and code.isdigit()


def _check(code: str) -> bool:
    return hashlib.sha256(_K + code.encode("ascii")).hexdigest() == _H


def _decrypt(code: str) -> str:
    key = hashlib.sha256(code.encode("ascii")).digest()
    plain = bytes(b ^ key[i % len(key)] for i, b in enumerate(_C))
    return plain.decode("utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        _usage()
        return 2
    code = argv[1]
    if not _validate(code):
        _usage()
        return 2
    if not _check(code):
        sys.stdout.write("STILL TRAPPED -- the door holds. Footsteps in the corridor.\n")
        return 1
    sys.stdout.write(_decrypt(code))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
