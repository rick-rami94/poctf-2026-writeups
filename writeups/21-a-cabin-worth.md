# A Cabin Worth

**Forensics · Wave 2 · 119 pts**

Artifact: a Joplin data directory — `database.sqlite`, `database.sqlite-wal`,
`database.sqlite-shm`. Imaged while Joplin was running, before a checkpoint. One
note was deleted the night of the disappearance.

## WAL carving

The live DB shows 4 notes. The deletion was written to the WAL but never
checkpointed, so earlier WAL frames still hold the pre-delete page.

Replay the WAL frame-by-frame and query each commit:

- commit 8 → **5 notes**
- commit 9 → 4 notes

The vanished one: *"Delacroix — 06/28 confirmation."*

## The encryption ("the medium is not who you think")

That note had `encryption_applied = 1`, body sitting in
`encryption_cipher_text` — a custom AES-256-GCM blob. The `settings` table
documents the scheme:

```
note.encryption.algorithm      AES-256-GCM
note.encryption.kdf            PBKDF2-HMAC-SHA256
note.encryption.kdf_iterations 200000
note.encryption.blob_layout    salt(16) || nonce(12) || ciphertext || tag(16), base64
note.password_hint             my good widdle boy!
```

## Password from the evidence

The hint points at a pet. The *shopping* note names him: **Horatio** ("kibble,
the salmon one he actually eats"). Password `horatio` derived the key and the
GCM tag verified:

```python
key = pbkdf2_hmac('sha256', b'horatio', salt, 200000, 32)
pt  = AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)
```

The plaintext is her Signal transcription — and it contains the flag.

## Flag

```
POCTF{REDACTED}
```

## Lesson

A pre-checkpoint WAL is a time machine: the "deleted" row is still on the old
page. The crypto was real, but the key was sitting in another note.
