# Known Issues — molecule-careful-bash

---

## Active Issues

*(None currently open. This section is updated when issues are filed.)*

---

## Recently Resolved

### [RESOLVED] OFFSEC-002: Token exfiltration patterns not blocked

**Severity:** P0 (security)
**Resolved in:** v1.0.1

**Symptoms:** The PreToolUse:Bash hook blocked destructive commands (force push, DROP TABLE, rm -rf) but did NOT block token exfiltration patterns. An LLM prompt injection could instruct the agent to execute:
- `cat ~/.gh_token`
- `cat /tmp/.git-credentials-cache`
- `env | grep token`

**Cause:** The REFUSE list in `pre-bash-careful.py` only covered git/SQL/rm commands. Token file reads and env variable grep patterns were not covered.

**Fix:** Added blocking for:
- Direct token file reads (`.gh_token`, `.auth_token`, `.git-credentials-cache`, etc.)
- `cat` of home-directory token paths (`~/.config/gh_token`, `/home/agent/.gh_token`)
- `env | grep` for secrets (case-insensitive: token, api_key, secret, auth, password, passwd)
- Generic credential file extensions in `cat` targets
- curl/wget credential redirect exfil

Also fixed: `rm -rf .git` check used `"/.git"` string search which never matched. Changed to regex `r"(^|\s)\.git(?:\s|$|/)"`.

**Prevention:** New security-sensitive patterns must be reviewed during plugin review. Add token-exfil test cases to any hook touching credential paths.

---

---

## How to Update This File

When a new issue is identified:
1. Add it under **Active Issues** using the template below
2. Include: symptom, cause (if known), workaround
3. When fixed, move to **Recently Resolved** and note the fix version

### Issue Template

```markdown
## [TICKET-NUMBER] <Short Title>

**Severity:** P0 / P1 / P2 / P3
**Status:** Workaround / Fix in progress / Fix available
**Affected versions:** All / vX.Y.Z+

**Symptoms:**
**Cause:**
**Workaround:**
**Fix (if available):**
```

---

## Severity Definitions

| Level | Description |
|---|---|
| P0 | Destructive command passes through; no block |
| P1 | Hook misidentifies safe command as destructive (false positive) |
| P2 | Command warned but not blocked (WARN instead of REFUSE) |
| P3 | Cosmetic or documentation issue |

---

## Reporting

Use the Molecule-AI/internal issue tracker. Tag with `plugin-molecule-careful-bash`.
