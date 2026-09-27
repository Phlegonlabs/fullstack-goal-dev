"""Administrator-selected HTTPS credentials for isolated publication Git calls.

Policy contains only an executable identity and exact endpoints, never secrets.
The helper owns credential storage and Git consumes its output privately.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
from pathlib import Path
from urllib.parse import urlsplit

from harness_core import ManifestError
from harness_git import _path_has_reparse_or_link, _trusted_executable, git_environment

POLICY_PATH = Path("/etc/product-delivery-harness/archive-push.credentials.json")
REGISTRY_PATH = r"SOFTWARE\ProductDeliveryHarness"
REGISTRY_VALUE = "ArchivePushCredentials"
UNBOUND = object()


def _policy_bytes() -> bytes | None:
    if os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_PATH, 0,
                                winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                value, kind = winreg.QueryValueEx(key, REGISTRY_VALUE)
        except FileNotFoundError:
            return None
        if kind != winreg.REG_SZ or not isinstance(value, str):
            raise ManifestError("ArchivePushCredentials must be a JSON REG_SZ")
        return value.encode("utf-8")
    if not POLICY_PATH.exists() and not POLICY_PATH.is_symlink():
        return None
    if _path_has_reparse_or_link(POLICY_PATH) or not POLICY_PATH.is_file():
        raise ManifestError("credential policy must be a non-link regular file")
    for path in (POLICY_PATH, *POLICY_PATH.parents):
        info = path.stat()
        if info.st_uid != 0 or info.st_mode & 0o022:
            raise ManifestError("credential policy must be root-owned and not group/world writable")
    return POLICY_PATH.read_bytes()


def credential_binding(url: str) -> dict[str, str] | None:
    if urlsplit(url).scheme != "https":
        return None
    try:
        payload = _policy_bytes()
        if payload is None:
            return None
        policy = json.loads(payload)
        if not isinstance(policy, dict) or set(policy) != {"endpoints", "helper", "sha256"}:
            raise ValueError("expected endpoints, helper, sha256")
        endpoints = policy["endpoints"]
        if not isinstance(endpoints, list) or not endpoints or any(
            not isinstance(item, str) or urlsplit(item).scheme != "https"
            or not urlsplit(item).hostname or urlsplit(item).username is not None
            or urlsplit(item).password is not None or urlsplit(item).query
            or urlsplit(item).fragment or any(c.isspace() for c in item)
            for item in endpoints
        ):
            raise ValueError("endpoints must be exact non-secret HTTPS URLs")
        if url not in endpoints:
            return None
        if not isinstance(policy["helper"], str) or not Path(policy["helper"]).is_absolute():
            raise ValueError("helper must be an absolute native executable path")
        helper = _trusted_executable(Path(policy["helper"]), "publication credential helper")
        digest = hashlib.sha256(helper.read_bytes()).hexdigest()
        if not isinstance(policy["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", policy["sha256"]):
            raise ValueError("helper sha256 must be lowercase hexadecimal")
        if digest != policy["sha256"]:
            raise ValueError("credential helper hash changed")
        return {"policy_sha256": hashlib.sha256(payload).hexdigest(),
                "helper": helper.as_posix(), "helper_sha256": digest, "endpoint": url}
    except (OSError, UnicodeError, ValueError) as exc:
        raise ManifestError("cannot validate administrator publication credential policy") from exc


def publication_environment(url: str, *, expected=UNBOUND, hooks_dir: str | None = None) -> dict[str, str]:
    """Return the isolated Git environment for publication reads and the push.

    Pass ``hooks_dir`` (a fresh empty directory) for a command that runs in the
    checkout, so repository hooks never run with publication credentials.
    """
    binding = credential_binding(url)
    if expected is not UNBOUND and binding != expected:
        raise ManifestError("publication credential policy/helper changed since request creation")
    env = git_environment()
    env = {key: value for key, value in env.items()
           if not key.upper().startswith(("GIT_TRACE", "GCM_TRACE", "GCM_DEBUG"))
           and key.upper() != "GIT_CURL_VERBOSE"}
    # An empty GIT_ASKPASS stops core.askPass and SSH_ASKPASS from running.
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never", GIT_ASKPASS="")
    config: list[tuple[str, str]] = []
    if binding is not None:
        # Git's helper shell receives only a quoted, OS-protected executable.
        # Credential values never enter this environment, argv, or evidence.
        helper = "!exec " + shlex.quote(binding["helper"])
        config += [("credential.helper", ""), ("credential.helper", helper),
                   ("credential.useHttpPath", "true"), ("http.followRedirects", "false")]
    # Command-line config outranks repository config.
    config.append(("core.fsmonitor", "false"))
    if hooks_dir is not None:
        config.append(("core.hooksPath", hooks_dir))
    env["GIT_CONFIG_COUNT"] = str(len(config))
    for index, (key, value) in enumerate(config):
        env[f"GIT_CONFIG_KEY_{index}"] = key
        env[f"GIT_CONFIG_VALUE_{index}"] = value
    return env
