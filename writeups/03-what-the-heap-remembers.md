# What the Heap Remembers

**Exploitation · Wave 5 · 100 pts**

A stripped Linux x86-64 ELF: an interactive slab allocator with
`alloc`/`free`/`write`/`read`. A flag sits in the binary, XOR'd against a key
the program derives at startup and keeps only in memory.

Ran it under Docker (`ubuntu:24.04`, glibc 2.39) since it's a Linux binary on macOS.

## Layout

The program uses a bump "arena" in `.bss`. At startup it:

1. Hashes the seed string `heap:131:2050:v2` (a Murmur-ish rolling hash, seed
   `0x9e3779b9`) into a 32-bit value `H`.
2. Seeds a glibc-style LCG (`x = x*0x41c64e6d + 0x3039`, output byte `(x>>16)&0xff`)
   with `H` and writes **59 keystream bytes** to arena offset 0.
3. Sets the arena cursor to 59 — so the keystream sits in `[0,59)` with **no
   handle tracking it**.

The flag ciphertext (59 bytes) lives in `.rodata` at `0x2080`. `flag = keystream ⊕ ciphertext`.

## The "lie"

`free` zeroes a block's data, but the cursor starts at 59 and `read`/`write`/`free`
only check `0 ≤ handle < cursor`, not that the handle is a real block. Handles
`0..58` index straight into the leftover keystream — the "humming" previous
occupant. That's the intended interactive leak.

## Shortcut taken

The derivation is fully static, so regenerate the keystream offline and XOR:

```python
M=0xffffffff; seed=b'heap:131:2050:v2'
eax=0x9e3779b9; edx=seed[0]; i=1
while True:
    edx=(edx^eax)&M; eax=(edx*0x5bd1e995)&M; eax=(eax^(eax>>15))&M
    if i>=len(seed): break
    edx=seed[i]; i+=1
ks=[]
for _ in range(59):
    eax=(eax*0x41c64e6d+0x3039)&M; ks.append((eax>>16)&0xff)
```

XOR against the `.rodata` ciphertext → flag. The leaked bytes from an
uninitialized `read` matched `ks[8:56]`, confirming the key.

## Flag

```
POCTF{131.2050.b1f0a6ae66c5c850.KONEK6EEXGJBLZHSLUPNGKG4G5}
```

## Lesson

"Freed and tidied" meant tidied for tracked blocks only. Memory the allocator
never handed out keeps humming — and an index check that trusts the number,
not the ownership, lets you read it.
