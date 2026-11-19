#!/usr/bin/env python3
"""Goertzel-based slow-FSK / tone decoder for buried-in-noise audio challenges.

Reads a mono WAV, splits it into fixed-length slots, and for each slot reports
the strongest candidate tone plus a winner/runner-up confidence ratio. Robust at
low SNR because it only tests the known candidate frequencies (no FFT leakage).

Example (POCTF 2026 "Frequency and Consequence"):
    base32 alphabet, freq(ch) = 500 + 50*index(ch), 500 ms slots.

    python3 fsk_decode.py signal.wav --slot-ms 500 \
        --base 500 --step 50 --alphabet ABCDEFGHIJKLMNOPQRSTUVWXYZ234567
"""
import argparse, math, struct, wave


def goertzel(seg, f, fr):
    coeff = 2.0 * math.cos(2.0 * math.pi * f / fr)
    s1 = s2 = 0.0
    for x in seg:
        s0 = x + coeff * s1 - s2
        s2, s1 = s1, s0
    return s1 * s1 + s2 * s2 - coeff * s1 * s2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--slot-ms", type=float, default=500.0)
    ap.add_argument("--base", type=float, default=500.0, help="freq of index 0")
    ap.add_argument("--step", type=float, default=50.0, help="Hz per index")
    ap.add_argument("--alphabet", default="ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
    ap.add_argument("--min-ratio", type=float, default=10.0,
                    help="slots below this confidence are treated as dead air")
    args = ap.parse_args()

    w = wave.open(args.wav, "rb")
    fr = w.getframerate()
    n = w.getnframes()
    raw = w.readframes(n)
    sw = w.getsampwidth()
    fmt = {1: "b", 2: "h", 4: "i"}[sw]
    s = struct.unpack("<%d%s" % (n, fmt), raw)

    slot = int(args.slot_ms / 1000.0 * fr)
    alpha = args.alphabet
    msg = []
    for i in range(n // slot):
        seg = s[i * slot:(i + 1) * slot]
        powers = [goertzel(seg, args.base + args.step * k, fr) for k in range(len(alpha))]
        order = sorted(range(len(alpha)), key=lambda k: powers[k], reverse=True)
        bi = order[0]
        ratio = powers[order[0]] / (powers[order[1]] + 1e-9)
        tag = alpha[bi] if ratio >= args.min_ratio else "."
        print("slot %2d  %s  idx=%2d  freq=%6.0f  ratio=%.1f"
              % (i, tag, bi, args.base + args.step * bi, ratio))
        if ratio >= args.min_ratio:
            msg.append(alpha[bi])
    print("\nMESSAGE:", "".join(msg))


if __name__ == "__main__":
    main()
