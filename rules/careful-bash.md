# molecule-careful-bash — Rules

## Overview

The `careful-bash` plugin intercepts bash commands via a pre-execution hook and
blocks commands matching a configurable blocklist. This document covers error
handling, logging, configuration, and release process.

---

## Error Handling

### Command Blocked

When a command matches a blocklist pattern, the plugin replaces the command
with:

```bash
echo "CAREFUL_BASH: blocked — pattern matched: <pattern-name>"
```

The agent receives this as stdout and should interpret it as a rejection. Do
**not** retry the same command — modify it or abandon the operation.

### Pattern Not in Blocklist But Suspicious

If the agent issues a command that is not on the blocklist but looks dangerous
(e.g., `dd if=/dev/zero of=/dev/sda`), there is no automated block in the
current version. File a new pattern request by opening an issue on this repo.

### Hook Registration Failure

If `pre-bash-careful` fails to register (runtime mismatch, missing hook API),
the plugin logs a `critical` error and **disables itself** rather than running
without the guardrail. The workspace continues without bash safety.

```
[CRIT] careful_bash: hook registration failed for runtime claude_code
[WARN] careful_bash: plugin disabled — bash safety NOT active
```

If you see this message, the bash safety guardrail is not running. Restore by
fixing the hook registration or pinning a compatible plugin version.

---

## Logging

| Event | Fields |
|---|---|
| `bash_blocked` | `workspace_id`, `pattern`, `command_preview`, `severity` |
| `bash_allowed` | (only in `--verbose` mode) |
| `careful_bash_disabled` | `workspace_id`, `reason` |

---

## Configuration

```yaml
careful_bash:
  enabled: true
  extra_patterns: []           # append org-specific patterns here
  disabled_for_roles: []       # (planned — not yet implemented)
  block_on_match: true          # set false to only warn (not yet implemented)
```

### Default Blocked Patterns

| Name | Pattern | Rationale |
|---|---|---|
| `force_main` | `git push --force.*main\|master` | Irreversible history rewrite |
| `rm_root` | `rm -rf /` | Complete file system deletion |
| `drop_prod` | `DROP TABLE.*prod` | Database destruction |
| `sudo_root` | `sudo su\|sudo -i` | Privilege escalation |
| `chmod_777` | `chmod -R 777` | Permissions misconfiguration |
| `pipe_sh` | `curl.*\|sh\|bash\|wget.*\|bash` | Piped script execution |
| `sys_halt` | `shutdown\|reboot\|halt` | System shutdown |

---

## Release Process

1. Update `plugin.yaml` version
2. Run the test suite:
   ```bash
   pytest tests/ -v
   ```
3. If adding new default patterns, add tests for them
4. Tag: `git tag vX.Y.Z && git push --tags`
5. Update org templates
6. Validate by running a blocked command in a dev workspace — it should produce
   the `CAREFUL_BASH:` echo and no output from the original command
