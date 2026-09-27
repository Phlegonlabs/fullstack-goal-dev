"""Non-secret policy binding and isolated credential helper wiring."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publication_credentials as subject
import push_archived_candidate as archive
import trusted_host_publication as host
from harness_core import ManifestError
from harness_git import git_executable

URL = "https://example.invalid/team/private.git"


class CredentialTests(unittest.TestCase):
    def test_real_git_uses_only_the_approved_helper_in_a_path_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix="credential fixture ") as temp:
            root = Path(temp)
            helper = root / "fixture helper.sh"
            helper.write_text("#!/bin/sh\nprintf 'username=fixture-user\\npassword=fixture-only\\n'\n", encoding="utf-8")
            helper.chmod(0o755)
            binding = {"helper": helper.as_posix(), "endpoint": URL,
                       "helper_sha256": hashlib.sha256(helper.read_bytes()).hexdigest(),
                       "policy_sha256": "a" * 64}
            with patch.object(subject, "credential_binding", return_value=binding):
                env = subject.publication_environment(URL, expected=binding)
            result = subprocess.run([git_executable(), "credential", "fill"], cwd=root, env=env,
                                    input="protocol=https\nhost=example.invalid\npath=team/private.git\n\n",
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(0, result.returncode, "isolated fixture helper failed")
            self.assertIn("username=fixture-user", result.stdout)
            self.assertIn("password=fixture-only", result.stdout)

    def test_policy_hash_endpoint_and_helper_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            helper = Path(temp) / "trusted helper.exe"
            helper.write_bytes(b"fixture executable")
            policy = {"endpoints": [URL], "helper": str(helper),
                      "sha256": hashlib.sha256(helper.read_bytes()).hexdigest()}
            def payload():
                return json.dumps(policy).encode()
            with patch.object(subject, "_policy_bytes", side_effect=payload), patch.object(
                subject, "_trusted_executable", return_value=helper
            ):
                binding = subject.credential_binding(URL)
                self.assertEqual(URL, binding["endpoint"])
                self.assertIsNone(subject.credential_binding(URL + "/other"))
                with patch.dict(os.environ, {"GIT_CONFIG_COUNT": "99", "GIT_ASKPASS": "evil",
                                             "GIT_CONFIG_GLOBAL": "evil", "GIT_TRACE_CURL": "trace.log",
                                             "GCM_TRACE_SECRETS": "1", "GIT_CURL_VERBOSE": "1"}):
                    env = subject.publication_environment(URL, expected=binding)
                self.assertEqual("5", env["GIT_CONFIG_COUNT"])
                self.assertEqual("http.followRedirects", env["GIT_CONFIG_KEY_3"])
                self.assertEqual("false", env["GIT_CONFIG_VALUE_3"])
                self.assertEqual(("core.fsmonitor", "false"), (env["GIT_CONFIG_KEY_4"], env["GIT_CONFIG_VALUE_4"]))
                self.assertEqual("", env["GIT_ASKPASS"])
                self.assertFalse(any(key.startswith(("GIT_TRACE", "GCM_TRACE")) for key in env))
                self.assertNotIn("GIT_CURL_VERBOSE", env)
                self.assertEqual("0", env["GIT_TERMINAL_PROMPT"])
                self.assertIn(helper.as_posix(), env["GIT_CONFIG_VALUE_1"])
                policy["endpoints"].append(URL + "/other")
                with self.assertRaisesRegex(ManifestError, "changed"):
                    subject.publication_environment(URL, expected=binding)
                helper.write_bytes(b"changed")
                with self.assertRaises(ManifestError):
                    subject.credential_binding(URL)

    def test_missing_policy_cannot_be_injected_or_enable_old_request(self):
        with patch.object(subject, "_policy_bytes", return_value=None):
            env = subject.publication_environment(URL, expected=None)
            self.assertEqual("1", env["GIT_CONFIG_COUNT"])
            self.assertEqual("core.fsmonitor", env["GIT_CONFIG_KEY_0"])
            self.assertFalse(any(value == "credential.helper" for value in env.values()))
        with patch.object(subject, "credential_binding", return_value={"helper": "new"}):
            with self.assertRaisesRegex(ManifestError, "changed"):
                subject.publication_environment(URL, expected=None)

    def _repo_with_remote(self, temp: Path) -> tuple[Path, Path]:
        root, remote = temp / "work", temp / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        for key, value in (("user.email", "test@example.invalid"), ("user.name", "Harness Test")):
            subprocess.run(["git", "config", key, value], cwd=root, check=True)
        subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", "base"], cwd=root, check=True)
        return root, remote

    def _script(self, path: Path, sentinel: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"#!/bin/sh\necho ran > '{sentinel.as_posix()}'\n", encoding="utf-8", newline="\n")
        path.chmod(0o755)

    def test_publication_push_never_runs_repository_hooks(self):
        with tempfile.TemporaryDirectory() as temp:
            root, remote = self._repo_with_remote(Path(temp))
            sentinel = Path(temp) / "hook-ran"
            self._script(root / ".git" / "hooks" / "pre-push", sentinel)
            local_hooks = Path(temp) / "local-hooks"
            self._script(local_hooks / "pre-push", sentinel)
            empty = Path(temp) / "no-hooks"
            empty.mkdir()
            for label, setup in (("default hooks dir", None), ("local core.hooksPath", str(local_hooks))):
                with self.subTest(label):
                    if setup is not None:
                        subprocess.run(["git", "config", "core.hooksPath", setup], cwd=root, check=True)
                    # Control: an ordinary push runs the planted hook.
                    subprocess.run(["git", "push", "-q", "--", str(remote), "HEAD:refs/heads/control"],
                                   cwd=root, check=True, capture_output=True)
                    self.assertTrue(sentinel.exists())
                    sentinel.unlink()
                    subprocess.run(["git", "push", "-q", "--delete", str(remote), "control"],
                                   cwd=root, check=True, capture_output=True)
                    sentinel.unlink(missing_ok=True)
                    env = subject.publication_environment(str(remote), expected=None, hooks_dir=str(empty))
                    pushed = subprocess.run([git_executable(), "--no-replace-objects", "push", "--", str(remote),
                                             "HEAD:refs/heads/published"], cwd=root, env=env,
                                            capture_output=True, text=True, timeout=60)
                    self.assertEqual(0, pushed.returncode, pushed.stderr)
                    self.assertFalse(sentinel.exists(), "repository pre-push hook ran during publication")
                    subprocess.run(["git", "push", "-q", "--delete", str(remote), "published"],
                                   cwd=root, check=True, capture_output=True)
                    sentinel.unlink(missing_ok=True)
            self.assertEqual([], list(empty.iterdir()))

    def test_publication_environment_neutralizes_repository_askpass(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _ = self._repo_with_remote(Path(temp))
            sentinel = Path(temp) / "askpass-ran"
            askpass = Path(temp) / "askpass.sh"
            self._script(askpass, sentinel)
            subprocess.run(["git", "config", "core.askPass", askpass.as_posix()], cwd=root, check=True)
            request = "protocol=https\nhost=example.invalid\npath=team/private.git\n\n"
            with patch.object(subject, "_policy_bytes", return_value=None):
                env = subject.publication_environment(URL, expected=None)
            # Control: without the empty GIT_ASKPASS the repository askpass runs.
            control = {key: value for key, value in env.items() if key != "GIT_ASKPASS"}
            subprocess.run([git_executable(), "credential", "fill"], cwd=root, env=control,
                           input=request, capture_output=True, text=True, timeout=30)
            self.assertTrue(sentinel.exists())
            sentinel.unlink()
            result = subprocess.run([git_executable(), "credential", "fill"], cwd=root, env=env,
                                    input=request, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(sentinel.exists(), "repository askpass ran during publication")

    def test_user_writable_or_relative_helper_is_rejected(self):
        for helper in ("relative-helper", str(Path.cwd() / "helper.exe")):
            payload = json.dumps({"helper": helper, "sha256": "a" * 64, "endpoints": [URL]}).encode()
            with patch.object(subject, "_policy_bytes", return_value=payload):
                with self.assertRaises((ManifestError, RuntimeError)):
                    subject.credential_binding(URL)

    def test_private_read_paths_pass_bound_credentials_to_isolated_git(self):
        binding = {"policy_sha256": "a" * 64, "helper": "/trusted/helper",
                   "helper_sha256": "b" * 64, "endpoint": URL}
        completed = subprocess.CompletedProcess([], 0, "a" * 40 + "\trefs/heads/run\n", "")
        for module, read in ((archive, lambda: archive._remote_state(Path.cwd(), URL, "refs/heads/run", credentials=binding)),
                             (host, lambda: host._remote_head(URL, "refs/heads/run", cwd=Path.cwd(), credentials=binding))):
            with patch.object(subject, "credential_binding", return_value=binding), patch.object(
                module, "git_executable", return_value="git"
            ), patch.object(module.subprocess, "run", return_value=completed) as run:
                self.assertEqual("a" * 40, read())
                env = run.call_args.kwargs["env"]
                self.assertEqual("5", env["GIT_CONFIG_COUNT"])
                self.assertNotEqual(Path.cwd(), run.call_args.kwargs["cwd"])
                self.assertIn(URL, run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
