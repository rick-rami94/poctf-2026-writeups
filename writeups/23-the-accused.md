# The Accused

**Forensics · Wave 8 · 141 pts (capstone) · ONE SHOT**

> **Status: answer derived; one-shot submission — confirm before transmitting.**

Three artifacts from the night of 2026-06-28. Identify Elena's session
(16-char `session_id`) **and** the operator who ran it. A wrong accusation is
final: zero points, no retries.

Artifacts: `halberd_outbox.mbox`, `apparatus-controller-var.tar.gz`
(session logs + `/etc/passwd` fragment), `halberd_telnet_wipe.pcap`.

## Operator map (from `/etc/passwd` GECOS)

| code | name |
|------|------|
| APP_OPR_3 | Cornelius Whitmore |
| APP_OPR_5 | Aldous Rennick |
| APP_OPR_7 | **Marion Halberd** |
| APP_OPR_9 | Nadia Boruvka |
| APP_OPR_12 | Rachel Ostler |

## Which session

Six logs; anonymized to operator/subject codes. One stands out — the night of
06/28, 22:14–23:03 UTC:

```
session_id=<redacted>
operator=APP_OPR_7          # Marion Halberd
subject=SBJ_14
frame=IV                    # all others frame=I
subject-selection-protocol=BYPASSED
safety-interlocks=OVERRIDE (operator)
... subject accepting ... subject response: transferred ... status=COMPLETE
```

## Corroboration (all three agree — not a frame-up)

- **mbox** — Halberd to the Steward: *"The Marchetti issue has been resolved…
  I have logged the session under the Frame IV catalog"* and *"The remaining
  records have been reduced."* Whitmore (APP_OPR_3) formally **refused** and
  disclaims all involvement.
- **pcap** — login as `halberd` from 192.168.140.14, then
  `rm session_*_marchetti.log*` / `rm *marchetti*` — a wipe of Marchetti's
  session that failed only because log-rotation had already stripped the
  `_marchetti` tag. The wipe listing includes `session_<redacted>.log.1`.

The operator code is confirmed by passwd, by Halberd's own emails, and by his
authenticated wipe. Not a spoof.

## Answer

- **session_id:** `<redacted>`
- **accused:** Marion Halberd

## Lesson

Anonymized logs plus a failed wipe plus a confession in the outbox: three
independent artifacts converging is what lets you spend a one-shot accusation.
