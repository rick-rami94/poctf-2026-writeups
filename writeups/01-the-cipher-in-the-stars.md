# The Cipher in the Stars

**Crypto · Wave 8 · 141 pts**

Two observatories run a QKD exchange. The transcript is a JSON of the public
channel: the receiver's per-photon basis and outcome, the sender's announced
state *pairs*, and parity rows for reconciliation.

Announcing pairs instead of bases is the tell: this is **SARG04**, not BB84.

## Transcript shape

- `photon_records`: 1400 × `{receiver_basis, receiver_outcome, announcement_id}`
- `pair_definitions`: 4 pairs, each one `+` state and one `×` state
- `parity_check_rows`: 128 rows of indices into the sifted key
- `syndrome_hex`: 128-bit syndrome

## Sift (SARG04)

For each photon, take the announced pair's state *in the basis the receiver
measured*. If the receiver's outcome differs from that state, the sent photon
could not have been it — so it was the **other** state in the pair, and the bit
is that state's value. Otherwise the photon is inconclusive → discard.

1400 photons → **356 conclusive bits**.

## Reconcile

The 128 parity rows only index positions 0–255, so the key is the first 256
sifted bits. Against the published syndrome, 15 checks failed. A plain
bit-flipping decoder cleared all 15 by flipping **5 bits** (~2% noise — matches
"the transmission was noisy").

The reading where the bit is the *basis* of the sent state left 68 failed
checks and would not decode, confirming the value interpretation.

## Flag

```
3be39d2648e9a913cab13b4def4f57414ba3651f7e29850ac4fadcc13ec0f68e
```

## Lesson

SARG04's whole security move is announcing pairs, not bases. The intercept is
solved by running the receiver's own disambiguation rule, then treating
reconciliation as ordinary syndrome decoding.
