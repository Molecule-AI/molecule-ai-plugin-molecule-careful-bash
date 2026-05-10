# molecule-careful-bash

Refuses destructive bash commands before they execute. Blocks commands that match a dangerous-pattern list — including `git push --force` to protected branches, `rm -rf` at root, and SQL `DROP` against production-like targets.

## How it works

The `PreToolUse:Bash` hook matches the command string against a deny-list. Matches block execution and surface a reason. Safe commands pass through unchanged.

## Denied patterns

| Pattern | Reason |
|---|---|
| `git push --force` to `main`/`master`/`production` | Irreversible history rewrite |
| `rm -rf /` or `rm -rf /*` | Complete filesystem deletion |
| `DROP DATABASE`, `DROP TABLE prod.*` | Irreversible data destruction |
| `shutdown`, `halt`, `init 0` | Host shutdown |

Custom patterns can be added via `settings-fragment.json`.

## Install

### In org template (org.yaml)

```yaml
plugins:
  - molecule-careful-bash
```

### From URL (community install)

```
github://Molecule-AI/molecule-ai-plugin-molecule-careful-bash
```

## Usage

No configuration needed. Install and the hook is active. To bypass for a specific command, disable the plugin temporarily via workspace settings.

## Settings

| Setting | Type | Description |
|---|---|---|
| `extra_refuse_patterns` | string[] | Additional command patterns to block |
| `mode` | `refuse` \| `warn` | Block or warn (default: refuse) |

## Hooks

- **PreToolUse:Bash** — matches command against deny-list, blocks or warns

## Architecture

```
hooks/
  pre-bash-careful.py   # Pattern matching, deny_pretooluse
  pre-bash-careful.sh    # Shell wrapper
  _lib.py                # Shared helpers
adapters/
  claude_code.py         # Registers hook
skills/
  careful-mode/          # Skill for managing patterns at runtime
settings-fragment.json   # Declares PreToolUse:Bash hook binding
```

## Runtime

- `claude_code` — primary

## Known issues

See [known-issues.md](known-issues.md).

## License

Business Source License 1.1 — © Molecule AI.
