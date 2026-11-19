#!/usr/bin/env python3
"""Recover files from a ZIP whose central directory + EOCD are destroyed.

Walks the intact local file headers directly (by their PK\\x03\\x04 signature)
and inflates each stream. Tolerates a one-byte smear of the 'P' (0x50) in every
signature by anchoring on the surviving \\x4b\\x03\\x04\\x14\\x00 bytes.

Used for: Structural Failure (POCTF 2026, Forensics, Wave 7).

Usage: zip_carve.py <mangled.zip> <out_dir>
"""
import struct, zlib, sys, os, re

def carve(path, out_dir):
    d = open(path, "rb").read()
    os.makedirs(out_dir, exist_ok=True)
    # Anchor on 'K\x03\x04\x14\x00' (version-needed 20); back up 1 to the header start.
    offs = [m.start() - 1 for m in re.finditer(b"\x4b\x03\x04\x14\x00", d)]
    if not offs:
        sys.exit("no local file headers found")
    for off in offs:
        (_sig, _ver, flags, method, _mt, _md, crc,
         csize, usize, fnl, efl) = struct.unpack("<IHHHHHIIIHH", d[off:off+30])
        name = d[off+30:off+30+fnl].decode("latin1", "replace")
        start = off + 30 + fnl + efl
        comp = d[start:start+csize]
        raw = zlib.decompress(comp, -15) if method == 8 else comp
        ok = (zlib.crc32(raw) == crc)
        safe = os.path.basename(name) or f"file_{off}"
        open(os.path.join(out_dir, safe), "wb").write(raw)
        print(f"[{'OK ' if ok else 'BAD'}] {name}  {usize} bytes"
              f"{'' if flags & 0x8 == 0 else '  (data-descriptor!)'}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    carve(sys.argv[1], sys.argv[2])
