# 14. Terms and Conditions Apply

- **Category:** Game Hacking (GH04) · **Wave:** 7 · **Points:** 141
- **Flag:** `POCTF{REDACTED}`

An "immortal" boss. All state lives on the server; the Godot client just sends
**HMAC-signed events** (`damage_dealt`, `heal_tick`, `flag_flip`, `entered_zone`)
signed with a per-session `session_key` from `/start`.

Extracted the embedded PCK (`tools/pck_extract.py`) and decompiled the `.gdc`
bytecode (`tools/gdc_decompile.py`). The boss is `is_invulnerable` (damage
ignored), but its server-side HP is a **signed int32** seeded at `2147483000` —
647 below `INT32_MAX`. The constants give it away: `HP_MAX_INT32 = 2147483647`,
and the heal zone *heals the boss* (the one input never meant to touch it, since
the boss normally refuses to enter).

No memory editing — I reproduced the protocol with the real session, so the
client-side watchdog never runs:

1. `/start` → nonce + `session_key`; HP = `2147483000`.
2. `flag_flip avoid_heal_zones=false`, then `entered_zone` (else `avoid_still_on`
   / `not_in_zone`). Neither counts as a terms violation — only `is_invulnerable`
   is guarded.
3. Spam `heal_tick {amount:40}` (a big heal is rejected as `implausible_amount`).
   ~17 ticks push HP past `INT32_MAX` → wraps to **−2147483616**.
4. `/finish` → server mints the marker. `seq` must be strictly monotonic per
   session or you get `stale_seq`.

Event signing:

```
msg  = "gh04-evt:%s:%d:%s:%s" % [session_nonce, seq, type, json_sorted(data)]
hmac = HMAC_SHA256(session_key, msg)   # session_key used as UTF-8 bytes
```

> A client-side anti-cheat is theatre when the trust boundary is a signed protocol
> you can replay from scratch. They trusted their own numbers; numbers have limits.
