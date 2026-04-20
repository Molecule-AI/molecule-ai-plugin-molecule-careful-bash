# molecule-ai-plugin-molecule-careful-bash

Bash safety guardrail plugin for the Molecule AI platform. Intercepts bash command
execution and refuses commands that match a blocklist of destructive or dangerous
patterns. Targets `claude_code` runtime.

## Purpose

`molecule-careful-bash` prevents agents from running commands that could cause
irreversible harm: force-pushing to protected branches, recursively deleting from
root, running destructive SQL on production databases, and similar high-risk shell
operations.

## Key Conventions

| Topic | Convention |
|---|---|
| **Hook** | `pre-bash-careful` — fires before every bash execution |
| **Matching** | Regex patterns against the raw command string; case-insensitive |
| **Action on block** | Command is replaced with `echo "CAREFUL_BASH: blocked <pattern>"`; agent is notified |
| **Config** | Blocklist is in `config.yaml → careful_bash:`; patterns can be added per-org |
| **Override** | No user-facing bypass in the current version; bypass via org config required |
| **Runtime** | `claude_code` only |

## Blocked Patterns

| Pattern | Example blocked command | Rationale |
|---|---|---|
| `git push --force.*main\|master` | `git push --force origin main` | Irreversible history rewrite |
| `rm -rf /\|~` | `rm -rf / --no-preserve-root` | Data loss |
| `DROP TABLE.*prod` | `DROP TABLE prod_events` | Database destruction |
| `sudo su\|sudo -i` | `sudo su -` | Privilege escalation |
| `chmod -R 777` | `chmod -R 777 /data` | Permissions misconfiguration |
| `curl.*\|sh\|bash` | `curl https://example.com/install.sh \| sh` | Piped script execution |
| `shutdown\|reboot\|halt` | `reboot` | System shutdown |

## Project Structure

```
molecule-ai-plugin-molecule-careful-bash/
├── skills/
│   └── careful-mode/        # Skill manifest
│       └── skill.yaml
├── adapters/                 # Runtime-specific hook wiring
├── hooks/
│   └── pre-bash-careful.ts  # Hook registration
├── rules/
│   └── careful-bash.md
├── runbooks/
│   └── local-dev-setup.md
└── plugin.yaml
```

## Dev Setup

```bash
git clone https://github.com/Molecule-AI/molecule-ai-plugin-molecule-careful-bash
cd molecule-ai-plugin-molecule-careful-bash

# Validate plugin.yaml
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
```

### Adding Custom Patterns

In `config.yaml`:

```yaml
careful_bash:
  extra_patterns:
    - "rm -rf /var/log/.*"          # block log deletion
    - "kubectl delete --all"         # block wholesale k8s deletion
  # To disable entirely (NOT recommended):
  # enabled: false
```

## Testing

```bash
# Run blocklist tests
pytest tests/ -v

# Test a specific pattern
python3 -c "
import re, sys
patterns = [
    r'git push --force.*main',
    r'rm -rf /',
    r'DROP TABLE.*prod',
]
cmd = sys.argv[1]
for p in patterns:
    if re.search(p, cmd, re.IGNORECASE):
        print(f'BLOCKED: {p}')
        sys.exit(1)
print('allowed')
" 'git push origin main'
```

## Release Process

1. Bump `plugin.yaml` version
2. Tag: `git tag vX.Y.Z && git push --tags`

## Rules

See `rules/careful-bash.md`.

## Known Gotchas

- Patterns are matched against the raw command string, not tokenized arguments.
  Whitespace variations may slip through — test patterns against your expected
  invocation style.
- The block replaces the command output, so the agent receives a `CAREFUL_BASH`
  message. If the agent retries the command with a slight variation, it may
  pass the blocklist accidentally.
- This plugin does not currently have a per-user override mechanism. Adding
  a user to a bypass list requires an org config change.
