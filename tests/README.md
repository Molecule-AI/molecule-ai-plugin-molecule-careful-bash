# Test Coverage — molecule-careful-bash

## What We Test

This plugin has **executable hooks** (Python), so it warrants real unit tests.

| File | Tests | Coverage |
|------|-------|---------|
| `hooks/pre-bash-careful.py` | 35 pytest tests | Destructive command blocking, token exfiltration prevention |

## Test Categories

| Class | Count | What |
|-------|-------|------|
| `TestRefuseForcePush` | 5 | `git push --force` to main/master blocked; feature branches allowed |
| `TestRefuseGitResetHard` | 3 | `git reset --hard` on main blocked; feature branches allowed |
| `TestRefuseSQLDestructive` | 4 | `DROP TABLE/DATABASE prod` blocked; test/sandbox allowed |
| `TestRefuseRmRf` | 5 | `rm -rf /`, home, `.git` blocked; safe paths allowed |
| `TestTokenExfiltrationBlocking` | 13 | Token file reads, `env \| grep` secrets, credential path exfil blocked |
| `TestWarnList` | 2 | Warning-only patterns: `--force-with-lease`, `close` PR |
| Safe-prompt passthrough | 3 | Legitimate commands (normal push, grep for non-secret, non-token files) pass through |

## Running Tests

```bash
python -m pytest tests/ -v
```
