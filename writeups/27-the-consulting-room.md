# The Consulting Room

**Crypto · Wave 3 · 125 pts**

A patient's AES-encrypted medical record, plus a "compliance verification"
endpoint that tells you whether an arbitrary blob is *structurally intact* for
your API token. That's a padding oracle wearing a lab coat.

## Shape of it

- Ciphertext: 80 bytes = **5 × 16-byte blocks** (block 0 is the IV).
- The token is flavor, not the key. I burned a few minutes ruling that out —
  token as AES-128/192/256 in every mode, base64-decoded, MD5/SHA-derived,
  OpenSSL `EVP_BytesToKey` passphrase, key/IV split, RC4/ChaCha20/Salsa20,
  repeating-XOR. All noise. There is **no offline shortcut**; the oracle is the
  attack.

## The oracle

```
POST /challenges/consulting-room/oracle
Authorization: Bearer <token>
{"record": "<hex>"}
```

- Valid PKCS#7 → `200 {"padding":"valid"}`
- Invalid → `400 {"padding":"invalid"}`

One bit per request. Classic CBC padding-oracle: for each ciphertext block,
forge the preceding block byte-by-byte, watch for valid padding, recover the
intermediate state `D_k(C_i)`, XOR with the real previous block → plaintext.
Guard the `pad == 1` false positive by perturbing the second-to-last byte.

## Solve

~255 guesses/byte × 16 × 4 blocks ≈ a few thousand requests (rate limit was
1000/min, so pace it; modest concurrency with early-stop keeps it under ~12k).
Recovered `POCTF{…}` with a clean 6-byte `0x06` pad at the tail.

See `tools/padding_oracle.py`.

## Flag

```
POCTF{REDACTED}
```

## Lesson

A verification endpoint that distinguishes *valid* from *invalid* padding is a
decryption endpoint. The "AES key" framing was misdirection — you never need
the key, only the one bit the server volunteers.
