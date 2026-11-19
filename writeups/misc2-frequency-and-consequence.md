# Frequency and Consequence

- **Category:** Misc (MISC02) · **Wave:** 2 · **Points:** 121
- **Target:** one per-team `signal.wav` (mono, 44.1 kHz)
- **Recover:** the 16-char base32 **nonce** (or full `POCTF{...}` — server takes either)

## Prompt

> The transmitter's been running for weeks. [...] What they hear changes with the
> frequency, not the pattern. [...] The recording is dominated by noise. Playback
> is unrewarding. But the signal is louder than the noise where it matters.
> → Find the carrier. Read what is on it.

Encoding given in the brief:

- 16 characters of base32 (`A–Z`, `2–7`).
- Each char = one **500 ms** slot, back-to-back, no gaps.
- Each char is a single tone: `freq(ch) = 500 + 50 × index(ch)` Hz, with
  `index(A)=0 … index(Z)=25, index(2)=26 … index(7)=31`.

So it's **slow FSK**: the data *is* the carrier frequency ("the medium is the
message"), buried at SNR ≈ −6 dB so naive playback/spectrogram-by-ear fails.

## Approach

Per 500 ms slot, test all 32 candidate frequencies with a **Goertzel filter**
(a single-bin DFT — cheap and exactly what you want when you know the frequencies
to look for) and pick the strongest. The known-frequency structure means the
signal beats the noise decisively even at −6 dB.

See `tools/fsk_decode.py`.

## Gotcha: find the real slots

The file was **9.0 s = 18 slots**, but there are only **16 tones**. Printing the
winner-vs-runner-up power ratio per slot made the boundary obvious:

```
slot  0  ...  ratio=1.0     <- dead air (no carrier)
slot  1   I   ratio=770.5
slot  2   I   ratio=526.8
 ...
slot 16   R   ratio=691.3
slot 17  ...  ratio=1.0     <- dead air
```

Slots 1–16 each win by 400–900× — unambiguous. Slots 0 and 17 are just noise
padding (ratio ≈ 1.0). Decoding only the loud slots prevents an off-by-one that a
naive "first 16 slots" read would cause.

## Result

16-char base32 nonce recovered from slots 1–16. Full form `POCTF{<nonce>}`.

`POCTF{...redacted — unique per team...}`

## Takeaways

- When the challenge *hands you the frequencies*, Goertzel >> FFT peak-picking:
  no leakage/windowing worries, trivially robust to noise.
- Always verify slot alignment by detection **confidence**, not by assuming the
  signal starts at t=0.
