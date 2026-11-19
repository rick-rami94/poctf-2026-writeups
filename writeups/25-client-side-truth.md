# Client-Side Truth

**Game Hacking · Wave 8 · 141 pts (capstone)**

The "server-authoritative" redesign. A 3D arena: boss on the floor, a tall
cylinder ("count room") in the middle. Floor shots do nothing; shots from
inside the cylinder count. "If the client decides what's true, the client can
lie." Fake anti-cheat is still client-side.

## Reversing

Same pipeline as Leap of Faith: carve the Godot 4.7.1 PCK, zstd-decompress the
`.gdc` scripts. `NetworkClient.gd` lists the real game API:

```
POST /challenges/client-side-truth/game/start      -> boss_hp, boss_pos, floor, count_room
POST /challenges/client-side-truth/game/pos         <- {ts, x, y, z}
POST /challenges/client-side-truth/game/fire         <- {ts, hit:true}   -> boss_hp
GET  /challenges/client-side-truth/game/state        -> {boss_hp, won, terms_violated}
GET  /challenges/client-side-truth/game/win_marker   -> {flag}
```

Auth: `Authorization: Bearer <game.token>`, `X-Team-ID: 2050`. Challenge id 136.

## The lie

The server tracks boss HP, but **the client reports its own position and hits**:

1. `start` → boss_hp 500. `count_room` is an elevated box (y≈21).
2. `pos {x,y,z}` → declare position *inside* the count_room. The watchdog
   anti-cheat (`is_invincible`, `is_invulnerable`, `hp>max_hp`) is purely
   client-side and never runs server-side against a scripted client.
3. `fire {ts, hit:true}` → server applies **50 damage per reported hit** using
   the last declared position. Ten hits → 0.
4. `state` → `won:true`, `terms_violated` never trips.
5. `win_marker` → flag.

Body shapes not fully in the string pool were found by fuzzing: `/pos` wants
`x,y,z` (not a `pos[]` array); `/fire` needs only `ts` + `hit`.

## Flag

```
POCTF{REDACTED}
```

## Lesson

Server-authoritative in name only. Authority over the *score* is not authority
over the *truth* — if the client narrates position and hits, it narrates the win.
