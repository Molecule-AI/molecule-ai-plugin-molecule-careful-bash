# molecule-careful-bash — Molecule AI Plugin

Plugin that refuses destructive bash commands (git push --force to main, rm -rf at root, DROP TABLE prod) via a PreToolUse:Bash hook.

## Overview

Safety plugin for `claude_code` runtime. Intercepts Bash tool calls before execution and refuses commands matching destructive patterns.

## Build and Test

```bash
# Validate plugin structure
python3 .molecule-ci/scripts/validate-plugin.py

# Install dependencies
pip install -r .molecule-ci/scripts/requirements.txt
```

## Project Structure

```
plugin.yaml             # Plugin manifest
SKILL.md                # agentskills.io spec
.claude/                 # Agent settings
.molecule-ci/
  scripts/
    validate-plugin.py  # plugin.yaml validator
    requirements.txt
runbooks/
  local-dev-setup.md
```

## Plugin Manifest

```yaml
name: molecule-careful-bash
version: 1.0.0
runtimes: [claude_code]
skills: [careful-mode]
hooks: [pre-bash-careful]
```

## Pre-commit Checklist

```bash
python3 .molecule-ci/scripts/validate-plugin.py && \
python3 -c "
import re, sys
with open('plugin.yaml') as f:
    content = f.read()
patterns = [r'sk.ant', r'ghp.', r'AKIA[A-Z0-9]']
if any(re.search(p, content) for p in patterns):
    print('FAIL: possible credentials found')
    sys.exit(1)
print('No credentials: OK')
" && echo "All checks passed"
```

## Release

Version bumps in plugin.yaml → tag → platform registry publishes.
