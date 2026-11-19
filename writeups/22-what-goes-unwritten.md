# What Goes Unwritten

**Forensics · Wave 3 · 120 pts**

> **Status: token derived, scoreboard acceptance unconfirmed.** Order of the two
> halves is inferred; the alternate order is noted below as fallback.

A Windows minidump from a library workstation (Firefox 119). Recover a
16-character base32 token (A–Z, 2–7). "Most strings lie."

## The catch

There is **no** 16-char base32 run anywhere in the dump — verified by an
exhaustive scan across ASCII, UTF-16LE (both byte alignments). The whole dump
contains exactly **two** 8-char base32 strings:

```
sessionRestoreToken:<redacted>
<redacted>|expires:1751659200
```

A 16-char token must be their concatenation, split across two memory artifacts.

## Order reasoning

In a `value|expires:ts` signed-token format, the value sits immediately before
`|expires`. `<redacted>` is the half touching `|expires` (trailing); `<redacted>` is
the leading half. Memory offset order agrees (<redacted> earlier).

## Answer (primary)

```
<redacted>
```

Fallback if rejected:

```
<redacted>
```

## Lesson

The decoys are the plaintext "session token expiration firefox" interned
strings. The real token was deliberately never written contiguously — you have
to rejoin it.
