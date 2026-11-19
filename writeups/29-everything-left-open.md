# Everything Left Open

**Forensics · Wave 1 · 67 pts**

A Firefox profile pulled from an unlocked laptop, "browser open, data entered
mid-form." The flag is *what she was about to submit* — and the brief nudges you
to mind the details.

## Profile layout

```
k-vance-profile/
  formhistory.sqlite
  logins.json
  places.sqlite
  prefs.js
  sessionstore-backups/recovery.jsonlz4
README.txt
```

`prefs.js` has `browser.sessionstore.resume_from_crash = true` → the live, mid-
edit tab state lives in **`recovery.jsonlz4`**.

## Decoding the session

`recovery.jsonlz4` is Firefox's **mozLz4**, not raw LZ4:

```
magic "mozLz40\0" (8 bytes) | uint32 LE decompressed size | LZ4 block
```

Strip the 12-byte header, `lz4.block.decompress(rest, uncompressed_size=size)`,
parse the JSON. The single open tab carries a `formdata` block:

```json
"formdata": { "id": {
  "artifact-flag": "POCTF{…}",
  "workstation": "hollis-office-desktop-elena",
  "case-notes": "…"
}}
```

`artifact-flag` is the field she was mid-submit on.

## The decoys ("details")

- `logins.json` "encrypted" creds are just **base64**:
  `ZS5tYXJjaGV0dGlAaG9sbGlzLmVkdQ==` → `e.marchetti@hollis.edu`,
  password `MnDayW3dnesd@y7`; plus a pastebin `anon-analyst / hunter2`. Bait.
- `formhistory.sqlite` / `places.sqlite` are flavor (search terms, history) —
  checked both for a competing `POCTF{…}`; there is none. Only one real flag.

## Flag

```
POCTF{REDACTED}
```

## Lesson

"Data entered mid-form" = `sessionstore-backups/recovery.jsonlz4`. Know the
mozLz4 header — standard LZ4 tools choke on the 12-byte Mozilla preamble. And
don't chase the obvious base64 logins when the prompt says *pay attention*.
