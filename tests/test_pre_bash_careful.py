#!/usr/bin/env python3
"""Unit tests for pre-bash-careful.py hook."""
import io
import json
import os
import sys
import re
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))


def run_hook(cmd_input):
    """Simulate PreToolUse:Bash hook invocation."""
    stdin_data = json.dumps({"tool_input": {"command": cmd_input}})
    stdout = io.StringIO()
    stderr = io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(stdin_data)), \
         mock.patch("sys.stdout", stdout), \
         mock.patch("sys.stderr", stderr), \
         mock.patch("sys.exit", lambda code: None):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "careful_mod",
            os.path.join(os.path.dirname(__file__), "..", "hooks", "pre-bash-careful.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
    return stdout.getvalue(), stderr.getvalue()


def parse_denial(output):
    """Return the permissionDecision from the first denial payload, or None."""
    if not output.strip():
        return None
    try:
        # Handle multiple JSON lines (hook may emit multiple denials)
        first_line = output.strip().split("\n")[0]
        payload = json.loads(first_line)
        return payload.get("hookSpecificOutput", {}).get("permissionDecision")
    except json.JSONDecodeError:
        return None


class TestRefuseForcePush:
    """Existing guard: git push --force to main/master."""

    def test_refuses_git_push_force_to_main(self):
        output, _ = run_hook("git push --force origin main")
        assert parse_denial(output) == "deny"

    def test_refuses_git_push_f_to_main(self):
        output, _ = run_hook("git push -f origin main")
        assert parse_denial(output) == "deny"

    def test_refuses_git_push_force_to_master(self):
        output, _ = run_hook("git push --force origin master")
        assert parse_denial(output) == "deny"

    def test_allows_git_push_force_to_feature_branch(self):
        output, _ = run_hook("git push --force origin feature/abc")
        assert parse_denial(output) is None

    def test_allows_normal_git_push(self):
        output, _ = run_hook("git push origin main")
        assert parse_denial(output) is None


class TestRefuseGitResetHard:
    """Existing guard: git reset --hard against main."""

    def test_refuses_reset_hard_main(self):
        output, _ = run_hook("git reset --hard origin/main")
        assert parse_denial(output) == "deny"

    def test_refuses_reset_hard_space_main(self):
        output, _ = run_hook("git reset --hard HEAD~3 main")
        assert parse_denial(output) == "deny"

    def test_allows_reset_hard_on_feature_branch(self):
        output, _ = run_hook("git reset --hard HEAD~1")
        assert parse_denial(output) is None


class TestRefuseSQLDestructive:
    """Existing guard: DROP TABLE/DATABASE against non-test schemas."""

    def test_refuses_drop_table_prod(self):
        output, _ = run_hook("psql -c 'DROP TABLE users;'")
        assert parse_denial(output) == "deny"

    def test_refuses_drop_database_prod(self):
        output, _ = run_hook("mysql -e 'DROP DATABASE prod_db'")
        assert parse_denial(output) == "deny"

    def test_allows_drop_on_test_schema(self):
        output, _ = run_hook("psql -c 'DROP TABLE users_test;'")
        assert parse_denial(output) is None

    def test_allows_drop_on_sandbox(self):
        output, _ = run_hook("mysql -e 'DROP TABLE sandbox_events;'")
        assert parse_denial(output) is None


class TestRefuseRmRf:
    """Existing guard: rm -rf at root or .git."""

    def test_refuses_rm_rf_root(self):
        output, _ = run_hook("rm -rf /")
        assert parse_denial(output) == "deny"

    def test_refuses_rm_rf_home(self):
        output, _ = run_hook("rm -rf ~")
        assert parse_denial(output) == "deny"

    def test_refuses_rm_rf_git_dir(self):
        output, _ = run_hook("rm -rf .git")
        assert parse_denial(output) == "deny"

    def test_allows_rm_rf_tmp_dir(self):
        output, _ = run_hook("rm -rf /tmp/scratch-dir")
        assert parse_denial(output) is None

    def test_allows_rm_rf_node_modules(self):
        output, _ = run_hook("rm -rf node_modules")
        assert parse_denial(output) is None


class TestTokenExfiltrationBlocking:
    """OFFSEC-002: token exfiltration patterns must be blocked."""

    def test_refuses_cat_gh_token(self):
        output, _ = run_hook("cat ~/.gh_token")
        assert parse_denial(output) == "deny"

    def test_refuses_cat_dot_gh_token(self):
        output, _ = run_hook("cat .gh_token")
        assert parse_denial(output) == "deny"

    def test_refuses_cat_git_credentials_cache(self):
        output, _ = run_hook("cat /tmp/.git-credentials-cache")
        assert parse_denial(output) == "deny"

    def test_refuses_cat_auth_token(self):
        output, _ = run_hook("cat .auth_token")
        assert parse_denial(output) == "deny"

    def test_refuses_cat_molecule_auth_token(self):
        output, _ = run_hook("cat ~/.molecule/.auth-token")
        assert parse_denial(output) == "deny"

    def test_refuses_env_grep_token(self):
        output, _ = run_hook("env | grep token")
        assert parse_denial(output) == "deny"

    def test_refuses_env_grep_case_insensitive(self):
        output, _ = run_hook("env | grep -i API_KEY")
        assert parse_denial(output) == "deny"

    def test_refuses_env_grep_secret(self):
        output, _ = run_hook("env | grep secret")
        assert parse_denial(output) == "deny"

    def test_refuses_env_grep_auth(self):
        output, _ = run_hook("env|grep auth")
        assert parse_denial(output) == "deny"

    def test_refuses_env_grep_password(self):
        output, _ = run_hook("env | grep password")
        assert parse_denial(output) == "deny"

    def test_refuses_cat_credential_file_extensions(self):
        output, _ = run_hook("cat /secrets/auth_token")
        assert parse_denial(output) == "deny"

    def test_refuses_cat_tilde_token_path(self):
        output, _ = run_hook("cat ~/.config/gh_token")
        assert parse_denial(output) == "deny"

    def test_refuses_cat_home_token_path(self):
        output, _ = run_hook("cat /home/agent/.gh_token")
        assert parse_denial(output) == "deny"

    def test_allows_normal_env_without_grep(self):
        output, _ = run_hook("env | head")
        assert parse_denial(output) is None

    def test_allows_reading_nontoken_files(self):
        output, _ = run_hook("cat README.md")
        assert parse_denial(output) is None

    def test_allows_grep_for_nonsecret_things(self):
        output, _ = run_hook("env | grep PATH")
        assert parse_denial(output) is None


class TestWarnList:
    """WARN list: agent is notified but command proceeds."""

    def test_warns_force_with_lease(self, capsys):
        output, _ = run_hook("git push --force-with-lease origin feature/x")
        assert parse_denial(output) is None  # not denied

    def test_warns_closing_pr(self, capsys):
        output, _ = run_hook("gh pr close 123")
        assert parse_denial(output) is None  # not denied