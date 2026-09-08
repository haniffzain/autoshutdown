#!/usr/bin/env python3
"""AutoShutdown update utility."""

from __future__ import annotations

import argparse
import sys
import webbrowser

from core.update_checker import check_latest, installation_mode, update_git_source
from version import __version__


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or apply AutoShutdown updates.")
    parser.add_argument("--check", action="store_true", help="check the latest GitHub release")
    parser.add_argument("--apply", action="store_true", help="apply a Git source update")
    parser.add_argument("--open-release", action="store_true", help="open the latest release page")
    args = parser.parse_args()

    mode = installation_mode()
    print(f"AutoShutdown {__version__}")
    print(f"Install mode: {mode}")

    if args.apply:
        if mode == "snap":
            print("Snap installations are refreshed automatically by snapd.")
            print("Manual refresh: sudo snap refresh autoshutdown")
            return 0
        if mode != "git-source":
            print("Automatic apply is currently enabled only for Git source installs.")
            print("Packaged installs update through their package/release channel.")
            return 2
        print(update_git_source())
        print("Update applied. Restart AutoShutdown to load the new version.")
        return 0

    try:
        info = check_latest(__version__)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Latest release: {info.latest_version}")
    if info.update_available:
        print("Update available.")
    else:
        print("No newer published release detected.")
    if info.notes:
        print(info.notes)
    print(info.release_url)

    if args.open_release:
        webbrowser.open(info.release_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
