# Health Is a Social Construct

**Game Hacking · Wave 4 · 138 pts**

A Godot top-down shooter. The final-room boss has "more HP than you'll ever chip
through, and hits harder than you can absorb." Not beatable by aim or patience —
*change the math*. No macOS build, so: reverse the Linux binary, patch it, run
it headless under emulation, let the game mint the flag itself.

## Reversing (same PCK/GDSC toolchain as Leap of Faith, #24)

Godot 4.7.1, PCK appended to the ELF (`GDPC` trailer). `tools/pck_extract.py`
parses the directory; `tools/gdc_decompile.py` strips the `GDSC` header and
zstd-decompresses each script's token/constant table.

Flag flow (`auth_check` + `FlagService`/`FlagToken.gd`, `Ticker.gd`):

```
POST /api/challenges/48/instance   -> { nonce }
POST /api/challenges/48/tick        (HMAC heartbeat, anti-cheat)
POST /api/challenges/48/complete    (+ X-POCTF-CHALLENGE-NONCE) -> { marker }
```

Challenge id **48**, from both `game.token` (`POCTF-GAME-2-48-…`) and
`team.key` (`TEAMKEY48-…`). The `2` in the token is a decoy.

Unlike #24, replaying the API directly is walled off by CSRF, and probing the
exemption looks like auth bypass — so I didn't. The clean path: **win the game
for real**; it authenticates and mints on its own.

## Patching (in place, no full repack)

Scenes are stored uncompressed in the PCK; `.gdc` are `GDSC` + zstd frames.
Trick: if a re-compressed `.gdc` is **smaller** than its slot, write it at the
same offset and **shrink the directory entry's size field** — no offset
cascade, no repack. Godot doesn't verify the per-file MD5 at load, so leave it.

Four edits:

| File | Change | Why |
|------|--------|-----|
| `bigboss.scn` | `max_hp` 1000 → 1 | one-shot the boss |
| `player.gdc` | HP const 100 → 100,000,000 | god mode |
| `enemy_basic.gdc` | damage consts 20/10 → 0 | stop contact kills |
| `bullet.gdc` | damage 10 → 1000 | one-shot enemies |

### The gotcha

First pass set `bullet` damage to 100000 and I kept dying at **full HP** in
room 2. Cause: **enemies fire the same bullet scene** — I'd buffed their shots
into instakills. Dropping it to 1000 (one-shots weak minions; trivial vs a 100M
HP player) fixed it. Rooms are spawner-capped (`spawn_total`), so they clear
when the last enemy dies; some hide behind walls, so you walk over and finish
them (god mode = no rush).

## Running it

amd64 Linux container, `Xvfb` + `llvmpipe` software GL, driven with `xdotool`,
screen read via screenshots. One launch gate: wait for network before starting
(the auth call fails `result=13` if DNS isn't up yet). Cleared all three rooms,
one-shot the boss → **YOU WIN** → the game's own `/complete` returned the
marker.

## Flag

```
POCTF{REDACTED}
```

## Lesson

The server **trusts the client** to only call `/complete` after a legitimate
win; every bit of "unwinnable" difficulty was a client-side number. Also: when
you buff a shared asset, check who else uses it — my own damage upgrade was
arming the enemies.
