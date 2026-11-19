#!/usr/bin/env python3
"""Generic CBC padding-oracle decryptor.

Point BASE/PATH at the oracle, set TOKEN + CT, run. The oracle must answer
HTTP 200 for valid PKCS#7 padding and non-200 (or an "invalid" body) otherwise.

Used for: The Consulting Room (POCTF 2026, Crypto, Wave 3).
"""
import binascii, json, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

BASE  = "https://CHANGE_ME"
PATH  = "/challenges/consulting-room/oracle"
TOKEN = ""                      # per-team bearer token (do not commit)
CT    = binascii.unhexlify("")  # IV || ciphertext, hex

_lock, _next, _count = threading.Lock(), [0.0], [0]
MIN_GAP = 0.066                 # ~900 req/min; stay under the rate limit

def _pace():
    with _lock:
        wait = _next[0] - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _next[0] = time.monotonic() + MIN_GAP
        _count[0] += 1

def oracle(raw: bytes) -> bool:
    body = json.dumps({"record": raw.hex()}).encode()
    for attempt in range(6):
        _pace()
        req = urllib.request.Request(BASE + PATH, data=body, method="POST",
              headers={"Authorization": f"Bearer {TOKEN}",
                       "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return False
            time.sleep((2 if e.code == 429 else 1) + attempt)
        except Exception:
            time.sleep(1 + attempt)
    raise RuntimeError("oracle unreachable")

def decrypt_block(prev: bytes, cur: bytes) -> bytes:
    inter = bytearray(16)                       # D_k(cur)
    pool = ThreadPoolExecutor(max_workers=12)
    for pad in range(1, 17):
        idx = 16 - pad
        tail = bytes(inter[idx + 1 + i] ^ pad for i in range(pad - 1))
        found = None
        for start in range(0, 256, 12):
            cand = list(range(start, min(start + 12, 256)))
            def test(g):
                forged = bytes(idx) + bytes([g]) + tail
                if oracle(forged + cur):
                    if pad == 1:                # guard the 0x02 0x02 false positive
                        probe = bytearray(forged); probe[14] ^= 0xFF
                        if not oracle(bytes(probe) + cur):
                            return None
                    return g
                return None
            for g, res in zip(cand, pool.map(test, cand)):
                if res is not None:
                    found = res; break
            if found is not None:
                break
        if found is None:
            pool.shutdown(wait=False)
            raise RuntimeError(f"no valid byte at pad={pad}")
        inter[idx] = found ^ pad
    pool.shutdown(wait=True)
    return bytes(a ^ b for a, b in zip(inter, prev))

def main():
    if "CHANGE_ME" in BASE or not TOKEN or not CT:
        sys.exit("Set BASE, TOKEN and CT first.")
    blocks = [CT[i:i+16] for i in range(0, len(CT), 16)]
    pt = b""
    for i in range(1, len(blocks)):
        pt += decrypt_block(blocks[i-1], blocks[i])
        print(f"[+] block {i}/{len(blocks)-1} ({_count[0]} reqs): {pt!r}", file=sys.stderr)
    n = pt[-1]
    if 1 <= n <= 16 and pt[-n:] == bytes([n]) * n:
        pt = pt[:-n]
    print(pt.decode("utf-8", "replace"))

if __name__ == "__main__":
    main()
