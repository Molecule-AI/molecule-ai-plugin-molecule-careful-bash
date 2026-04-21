# Local Development Setup

This runbook covers setting up a local development environment for
`molecule-careful-bash`.

---

## Prerequisites

- Python 3.11+
- `gh` CLI authenticated
- Write access to `Molecule-AI/molecule-ai-plugin-molecule-careful-bash`

---

## Clone & Bootstrap

```bash
git clone https://github.com/Molecule-AI/molecule-ai-plugin-molecule-careful-bash.git
cd molecule-ai-plugin-molecule-careful-bash
```

---

## Validating Plugin Structure

```bash
# YAML structure
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
echo "plugin.yaml OK"

# Check all hook paths exist
python3 -c "
import yaml, os
with open('plugin.yaml') as f:
    data = yaml.safe_load(f)
for hook in data.get('hooks', []):
    path = f'hooks/{hook}/hook.json'
    exists = os.path.exists(path)
    print(f'[{\"OK\" if exists else \"MISSING\"}] {path}')
for skill in data.get('skills', []):
    path = f'skills/{skill}/SKILL.md'
    exists = os.path.exists(path)
    print(f'[{\"OK\" if exists else \"MISSING\"}] {path}')
"
```

---

## Testing the Guard Locally

The harness wrapper is provided by the Molecule AI platform at runtime. To test:

1. Install the plugin in a test workspace
2. Issue a guarded command (e.g., `rm -rf /*`) via the Bash tool
3. Verify it is REFUSE'd with a clear error message
4. Issue a warning command (e.g., `ALTER TABLE prod_main`) and verify it warns

---

## Simulating Guard Behaviour

```python
# Minimal guard logic for local simulation
COMMANDS = ["git push --force origin main", "rm -rf /", "DROP TABLE prod_main"]

def check(command: str) -> str:
    if "git push --force" in command and "main" in command.split("git push --force")[1]:
        return "REFUSE"
    if command.strip().startswith("rm -rf /"):
        return "REFUSE"
    if "DROP TABLE" in command:
        return "REFUSE"
    return "ALLOW"

for cmd in COMMANDS:
    print(f"{cmd!r}: {check(cmd)}")
```

---

## Troubleshooting

### Guard not firing

- Verify `hooks/pre-bash-careful/hook.json` is correctly named
- Check the hook is registered in `plugin.yaml`
- Verify the workspace runtime is `claude_code`

### False positive on safe command

- The guard uses pattern matching — a safe command that looks like a dangerous
  one will be blocked
- Report false positives so the pattern can be refined

---

## Related

- `hooks/pre-bash-careful/hook.json` — hook definition
- `skills/careful-mode/SKILL.md` — agent-facing skill documentation
