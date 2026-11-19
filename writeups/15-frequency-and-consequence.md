# 15. Frequency and Consequence

- **Category:** Misc (MISC02) · **Wave:** 2 · **Points:** 121
- **Nonce:** `<redacted — 16-char base32 nonce>` (submit bare, or wrapped as `POCTF{REDACTED}`)

One per-team `signal.wav` (mono, 44.1 kHz, SNR ≈ −6 dB). Slow **FSK**: 16 base32
chars, one per 500 ms slot, `freq(ch) = 500 + 50×index(ch)` Hz. The data *is* the
carrier frequency, so playback-by-ear is useless.

Per 500 ms slot, test all 32 candidate frequencies with a **Goertzel** filter and
take the strongest. Single-bin DFT on known frequencies beats the noise cleanly.
Reusable decoder: [`tools/fsk_decode.py`](../tools/fsk_decode.py).

Gotcha: the file is 9.0 s = **18** slots but only **16** tones. The winner/
runner-up power ratio makes it obvious — slots 0 and 17 are dead air (ratio ≈ 1),
slots 1–16 each win by 400–900×. Decoding by confidence, not by "first 16 slots,"
avoids an off-by-one.

```
slot  0  .   ratio=1.0      <- dead air
slot  1  I   ratio=770.5
 ...
slot 16  R   ratio=691.3
slot 17  .   ratio=1.0      <- dead air
```

> When the challenge hands you the frequencies, Goertzel beats FFT peak-picking —
> and verify slot alignment by detection confidence, never by assuming t=0.
