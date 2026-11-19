# Structural Failure

**Forensics · Wave 7 · 140 pts**

A ZIP "sabotaged after the fact" — the End-of-Central-Directory record and every
central directory entry overwritten with garbage. Standard tools refuse it. But
the **local file headers and compressed streams at the top survived**.

## Two layers

The provided archive is intact and holds `README.txt` + the real victim,
`meridian-correspondence.zip`. That inner ZIP is the mangled one.

## The actual damage

`unzip` fails the signature check, and a scan for `PK\x03\x04` finds nothing.
Hexdump shows why: every ZIP signature's **first byte `0x50` ('P') was flipped
to `0xea`**, so `PK\x03\x04` → `\xea\x4b\x03\x04`. The central dir + EOCD are
fully garbage, but the local headers are otherwise untouched — filenames in
cleartext (`01_halberd_correspondence.txt`, `03_marchetti_annotations.md`).

## Recovery

Ignore the dead central directory entirely. Locate the three local headers by
their surviving `\x4b\x03\x04\x14\x00` bytes, read the fixed-offset fields
(flags `0` → sizes are inline, no data-descriptor), carve `csize` bytes, inflate
raw deflate (`zlib.decompress(data, -15)`). **All three CRC32s matched** — a
perfect recovery. See `tools/zip_carve.py`.

Read all three files; the token is the docket ref in Elena's own annotations:

```
# MARCHETTI 2026-14 docket ref: <16 base32 chars>
```

## Flag

```
POCTF{REDACTED}
```

## Lesson

A ZIP's central directory is an *index*, not the data. Local file headers +
deflate streams are self-sufficient — you can rebuild an archive from them alone.
Knowing the four-byte signatures (`50 4B 03 04`) is enough to spot a one-byte
smear and walk past it.
