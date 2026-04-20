# Known Issues

> Living document for molecule-ai-plugin-molecule-careful-bash.

---

## 1. Pattern matching is string-level, not AST-level

**Severity:** Medium
**Affected versions:** All stable
**Status:** Known; tracked in `#cb-5`

Patterns are matched with `re.search` on the raw command string. A command like
`git push --force -o main` (using the `-o` long option) passes the blocklist even
though `--force` is present. Similarly, commands split across lines or using
variables may evade detection.

**Workaround:** Test all expected command forms against the blocklist before
deploying. Add patterns for any variant forms you observe agents using.

---

## 2. No audit log of blocked commands

**Severity:** Medium
**Affected versions:** All stable
**Status:** Known; tracked in `#cb-11`

Blocked commands are replaced with an `echo` and the agent receives a notification,
but the event is not written to the molecule audit ledger. Operators cannot
retrieve a history of blocked commands for security review.

**Workaround:** None for now. Audit ledger integration is tracked in `#cb-11`.

---

## 3. No per-user or per-org override mechanism

**Severity:** Medium
**Affected versions:** All stable
**Status:** Known; tracked in `#cb-17`

The plugin has no user-level bypass. Adding a bypass requires an org config change
that affects all users in the org. There is no `careful_bash.disabled_for_roles`
config option.

**Workaround:** Use org config to add bypass for trusted roles. A per-user override
via workspace config is planned.

---

## 4. `curl | sh` pattern may have false negatives with alternate pipes

**Severity:** Low
**Affected versions:** All stable
**Status:** Known; tracked in `#cb-23`

The piped-script detection pattern `curl.*\|sh\|bash` does not catch
`curl ... | sh` with extra spaces, `curl ... > /tmp/s.sh && sh /tmp/s.sh`, or
`wget -qO- ... | bash`. These variants are increasingly common in install scripts.

**Workaround:** Add `curl.*>.*\.sh.*sh` and `wget.*\|bash` to `extra_patterns`
in your config until the default pattern is updated.

---

## 5. Commands blocked inside interactive shells are not caught

**Severity:** Low
**Affected versions:** All stable
**Status:** Known; tracked in `#cb-29`

If the agent starts an interactive shell (`bash`, `zsh`, `python -i`) and then
types a blocked command inside the shell, the plugin's pre-hook only sees the
shell invocation, not the inner command. The command executes un-checked.

**Workaround:** Configure the agent's system prompt to prohibit interactive shell
use, or add shell names to the blocklist.
