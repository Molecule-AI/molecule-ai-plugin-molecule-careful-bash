# molecule-careful-bash — Destructive Bash Guard

`molecule-careful-bash` is a **PreToolUse:Bash safety hook** that refuses
destructive commands: `git push --force` to main, `rm -rf /` at root level,
`DROP TABLE` on production databases.

**Version:** 1.0.0
**Runtime:** `claude_code`

---

## Repository Layout

```
molecule-careful-bash/
├── plugin.yaml              — Plugin manifest
├── hooks/
│   └── pre-bash-careful/
│       └── hook.json        — PreToolUse:Bash hook definition
└── skills/
    └── careful-mode/       — Skill documentation for agents
```

---

## Guarded Commands

The hook intercepts Bash tool calls matching these patterns:

| Pattern | Action |
|---|---|
| `git push --force` to `main` or `master` | REFUSE — hard block |
| `rm -rf /` or `rm -rf /*` | REFUSE — hard block |
| `DROP TABLE` + prod database name | REFUSE — hard block |
| `ALTER TABLE` + prod database name | WARN |
| `git push --force` to non-main branches | WARN |

`REFUSE` means the command is blocked and the agent is told why.
`WARN` means the agent is warned but the command proceeds.

---

## Configuration

In workspace `config.yaml`:

```yaml
careful_bash:
  enabled: true
  prod_db_patterns: ["prod_", "production_", "main_"]
```

---

## Development

### Prerequisites

- Python 3.11+
- `gh` CLI authenticated
- Write access to `Molecule-AI/molecule-ai-plugin-molecule-careful-bash`

### Setup

```bash
git clone https://github.com/Molecule-AI/molecule-ai-plugin-molecule-careful-bash.git
cd molecule-ai-plugin-molecule-careful-bash

# YAML validation
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
```

### Pre-Commit Checklist

```bash
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"

python3 -c "
import re, sys
with open('plugin.yaml') as f:
    content = f.read()
patterns = [r'sk.ant', r'ghp.', r'AKIA[A-Z0-9]']
if any(re.search(p, content) for p in patterns):
    print('FAIL: possible credentials found')
    sys.exit(1)
print('No credentials: OK')
"
```

---

## Release Process

1. Review changes: `git log origin/main..HEAD --oneline`
2. Bump `version` in `plugin.yaml` (semver)
3. Commit: `chore: bump version to X.Y.Z`
4. Tag and push: `git tag vX.Y.Z && git push origin main --tags`
5. Create GitHub Release with changelog

---

## Known Issues

See `known-issues.md` at the repo root.
