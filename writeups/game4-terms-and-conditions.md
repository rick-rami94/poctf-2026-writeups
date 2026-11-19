# Terms and Conditions Apply

- **Category:** Game Hacking (GH04) · **Wave:** 7 · **Points:** 141
- **Flag format:** `POCTF{...}` (unique per team — redacted below)

## Prompt

> You are standing in the Arena. The boss across from you is faster, stronger,
> and immortal. You cannot kill it by hitting it harder. You cannot kill it at
> all — the game will not let you — not from the outside. [...] The Terms are
> enforced, but the Terms were written by someone who trusted their own numbers.
> Numbers have limits.

A ~105 MB Godot game binary plus a small per-team credentials bundle
(`game.token`, `team.key`) that the game reads from its own directory to sign a
session.

## Recon

The Linux build is an ELF with an **embedded Godot PCK** (`GDPC` magic near the
tail, length stored in the last 12 bytes). Carve it out and extract the files
(`tools/pck_extract.py`). The gameplay logic ships as Godot 4.x **GDScript
bytecode** (`.gdc`), which decompiles cleanly (`tools/gdc_decompile.py`).

Key scripts recovered:

- `NetworkClient.gd` — all game state lives on a **server**
  (`pointeroverflowctf.com/challenges/terms-conditions/game`). The client sends
  **HMAC-signed events** (`damage_dealt`, `heal_tick`, `flag_flip`,
  `entered_zone`, …) signed with a per-session `session_key` returned by `/start`.
- `boss.gd` — the boss is `is_invulnerable = true`, so `damage_dealt` is ignored.
  Giveaway constants:
  ```gdscript
  const HP_MAX_INT32 : int = 2147483647
  const HP_OVERFLOW  : int = 4294967296
  var _server_hp : int = 2147483000   # starts 647 below INT32_MAX
  ```
- `heal_zone.gd` — the heal zone **heals the boss** (the one input never meant to
  touch it: the boss normally refuses to enter via `avoid_heal_zones = true`).
- `arena.gd` — when the **server** reports `hp < 0`, the boss "overflow-dies" and
  the client calls `/finish` to collect the flag marker.
- `watchdog.gd` — bans you (client-side only) if `is_invulnerable` /
  `avoid_heal_zones` are edited in *memory*. Irrelevant if you speak the protocol
  directly instead of patching the running process.

## Vulnerability

"They trusted their own numbers — numbers have limits." The boss's server-side HP
is a **signed 32-bit int** starting at `2,147,483,000`. Heals are the only
unguarded input (the boss is never supposed to be healed). Push HP past
`INT32_MAX = 2,147,483,647` and it **wraps negative = dead**.

## Exploit

Reproduce the signed-event protocol with the legitimate team session — no memory
editor, so the watchdog never runs.

Event signing (from `NetworkClient._dispatch_event`):

```
msg = "gh04-evt:%s:%d:%s:%s" % [session_nonce, seq, type, json_sorted(data)]
hmac = HMAC_SHA256(session_key, msg)   # session_key used as UTF-8 bytes
```

`seq` must be **strictly monotonic per session** (server tracks it; out-of-order
→ `stale_seq`). `json_sorted` sorts keys and emits bools/ints unquoted.

Chain:

1. `POST /start` → `session_nonce`, `session_key`, and state (`hp = 2147483000`).
2. `flag_flip {name: "avoid_heal_zones", value: false}` — server returns `ok`;
   does **not** count as a terms violation (only `is_invulnerable` is guarded).
3. `entered_zone {}` → server sets `in_heal_zone = true`.
   (Skipping steps 2–3 yields `avoid_still_on` / `not_in_zone`.)
4. Spam `heal_tick {amount: 40}`. A single large heal is rejected as
   `implausible_amount`, so pump the realistic 40/tick value ~17 times. HP crosses
   `INT32_MAX` and wraps to **−2,147,483,616**.
5. `POST /finish` → issues the per-team `marker` (the flag).

```
start hp= 2147483000
flip    -> ok
enter   -> ok, in_heal_zone=true
heal x17-> hp wraps to -2147483616
FINISH  -> {"marker":"POCTF{...REDACTED...}","ok":true}
```

## Flag

`POCTF{...redacted — unique per team...}` · nonce recovered from `/finish`.

## Takeaways

- A client-side anti-cheat watchdog is meaningless when the trust boundary is a
  signed network protocol you can replay from scratch.
- Mixing a near-`INT32_MAX` sentinel HP with an unbounded additive input is the
  whole bug — classic signed-overflow "win condition."
