# molecule-careful-bash — Local Dev Setup

## Prerequisites

- `git`
- Python 3.11+ (for YAML validation)
- A local or staging Molecule platform
- A workspace with the `claude_code` runtime

## Clone and Validate

```bash
git clone https://github.com/Molecule-AI/molecule-ai-plugin-molecule-careful-bash
cd molecule-ai-plugin-molecule-careful-bash

python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('skills/careful-mode/skill.yaml'))"
```

## Point Your Org Template at a Dev Branch

```yaml
plugins:
  - github://Molecule-AI/molecule-ai-plugin-molecule-careful-bash@<branch>
```

## Test the Blocklist

### Blocked Commands (should produce CAREFUL_BASH echo)

```bash
# Should be blocked — CAREFUL_BASH: blocked
git push --force origin main

# Should be blocked
rm -rf /

# Should be blocked
DROP TABLE prod_events;
```

If any of these execute without the `CAREFUL_BASH:` message, the plugin is not
loaded correctly.

### Allowed Commands (should execute normally)

```bash
# Should be allowed
ls -la /tmp

# Should be allowed
git push origin feature/my-branch

# Should be allowed
rm -rf /tmp/test-dir
```

## Add a Custom Pattern

In `config.yaml`:

```yaml
careful_bash:
  extra_patterns:
    - "kubectl delete --all.*namespace"    # block wholesale k8s deletion
    - "docker system prune -a"             # block image cache wipe
```

## Inspect Audit Events

```bash
# List recent blocked events
mol platform audit query --since 1h | grep bash_blocked
```

## Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| Blocked command still runs | Plugin not loaded in workspace | Restart workspace with plugin in org template |
| Pattern `curl | sh` misses variant | Pattern is string-level not AST | Add to `extra_patterns` |
| No audit log entry | Audit ledger not configured | Configure `audit:` in config.yaml |
| Hook not registered | Runtime mismatch | Verify `plugin.yaml` `runtimes:` includes your runtime |
