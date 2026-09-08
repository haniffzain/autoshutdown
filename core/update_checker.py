"""Update detection and source-update helpers for AutoShutdown."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPOSITORY = "haniffzain/autoshutdown"
LATEST_RELEASE_API = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
RELEASES_URL = f"https://github.com/{REPOSITORY}/releases/latest"


@dataclass(frozen=True)
class UpdateInfo:
    current_version: str
    latest_version: str
    update_available: bool
    release_url: str
    release_name: str = ""
    notes: str = ""


def _version_tuple(value: str) -> tuple[int, ...]:
    cleaned = value.strip().lstrip("vV")
    numbers = re.findall(r"\d+", cleaned.split("-", 1)[0])
    return tuple(int(part) for part in numbers[:4]) or (0,)


def is_newer(latest: str, current: str) -> bool:
    a = list(_version_tuple(latest))
    b = list(_version_tuple(current))
    width = max(len(a), len(b))
    a.extend([0] * (width - len(a)))
    b.extend([0] * (width - len(b)))
    return tuple(a) > tuple(b)


def installation_mode() -> str:
    if os.environ.get("SNAP"):
        return "snap"
    if getattr(sys, "frozen", False):
        return "windows-exe" if os.name == "nt" else "frozen"
    root = Path(__file__).resolve().parents[1]
    if (root / ".git").exists():
        return "git-source"
    if str(root).startswith("/opt/autoshutdown"):
        return "deb"
    return "source"


def check_latest(current_version: str, timeout: float = 5.0) -> UpdateInfo:
    request = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "AutoShutdown-UpdateChecker",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return UpdateInfo(current_version, current_version, False, RELEASES_URL, notes="No GitHub release has been published yet.")
        raise RuntimeError(f"GitHub update check failed: HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unable to check for updates: {exc}") from exc

    tag = str(payload.get("tag_name") or "").strip()
    if not tag:
        raise RuntimeError("Latest GitHub release does not contain a version tag.")
    latest = tag.lstrip("vV")
    return UpdateInfo(
        current_version=current_version,
        latest_version=latest,
        update_available=is_newer(latest, current_version),
        release_url=str(payload.get("html_url") or RELEASES_URL),
        release_name=str(payload.get("name") or tag),
        notes=str(payload.get("body") or ""),
    )


def git_root() -> Path | None:
    root = Path(__file__).resolve().parents[1]
    if (root / ".git").exists():
        return root
    return None


def update_git_source() -> str:
    root = git_root()
    if root is None:
        raise RuntimeError("This AutoShutdown installation is not a Git checkout.")

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if status.returncode != 0:
        raise RuntimeError(status.stderr.strip() or "Unable to inspect the Git working tree.")
    if status.stdout.strip():
        raise RuntimeError("Local changes detected. Commit or stash them before auto-update.")

    result = subprocess.run(
        ["git", "pull", "--ff-only"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        raise RuntimeError(output or "Git update failed.")
    return output or "Source is already up to date."
