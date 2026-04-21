# Local Development Setup

## Prerequisites

- Python 3.11+
- `pip`

## Setup

```bash
git clone https://github.com/Molecule-AI/molecule-ai-plugin-molecule-careful-bash.git
cd molecule-ai-plugin-molecule-careful-bash
pip install -r .molecule-ci/scripts/requirements.txt
python3 .molecule-ci/scripts/validate-plugin.py
```

## Validating

```bash
python3 .molecule-ci/scripts/validate-plugin.py
```

Expected: `✓ plugin.yaml valid: molecule-careful-bash v1.0.0`

## Pre-commit

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
