# Leap of Faith

**Game Hacking · Wave 2 · 87 pts**

A Godot game. The jump height is "not quite high enough" to reach the last
platform — the intended solve is editing the running game's memory. No macOS
build shipped, so I reversed the Linux binary instead.

## Reversing the PCK

Godot 4.7.1. The game data is a PCK appended to the executable (`GDPC` trailer).

1. Parse the embedded PCK directory (pack format 4): trailer gives pck size →
   start → directory offset.
2. Extract the `.gdc` scripts. They look encrypted but the header is
   `GDSC` + version + decompressed-size, then a **zstd** stream (`28 b5 2f fd`).
3. Decompress → readable GDScript token/constant tables.

## The minting protocol

`auth_check.gd` and `FlagService` (`FlagToken.gd`) reveal everything:

```
GET  /api/challenges/47/instance   headers: X-POCTF-GAME-TOKEN, X-POCTF-TEAM-KEY
     -> { nonce }
POST /api/challenges/47/complete   headers: + X-POCTF-CHALLENGE-NONCE, body {}
     -> { marker }   # the flag
```

Challenge id `47` comes straight from both `game.token`
(`POCTF-GAME-1-47-…`) and `team.key` (`TEAMKEY47-…`).

**Reaching the goal is only a client-side trigger** — the server never checks
that you jumped. So replay the two calls:

```bash
NONCE=$(curl -s .../47/instance -H "X-POCTF-GAME-TOKEN: $GT" -H "X-POCTF-TEAM-KEY: $TK" | jq -r .nonce)
curl -s -X POST .../47/complete -H "X-POCTF-GAME-TOKEN: $GT" -H "X-POCTF-TEAM-KEY: $TK" \
     -H "X-POCTF-CHALLENGE-NONCE: $NONCE" -H 'Content-Type: application/json' --data '{}'
```

## Flag

```
POCTF{REDACTED}
```

## Lesson

The physics was a red herring. The server minted the flag on a nonce and an
authenticated "I finished" — never on proof you actually finished.
