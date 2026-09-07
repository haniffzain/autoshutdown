#!/usr/bin/env python3
"""AutoShutdown - lightweight cross-platform shutdown and logout scheduler."""

from __future__ import annotations

import argparse
import getpass
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta


DURATION_RE = re.compile(r"^(\d+)([smh])$", re.IGNORECASE)


def parse_duration(value: str) -> int:
    """Convert 30s/15m/2h into seconds."""
    match = DURATION_RE.fullmatch(value.strip())
    if not match:
        raise argparse.ArgumentTypeError("Gunakan format seperti 30s, 15m atau 2h.")

    amount = int(match.group(1))
    unit = match.group(2).lower()
    multiplier = {"s": 1, "m": 60, "h": 3600}[unit]
    return amount * multiplier


def seconds_until(clock_time: str) -> int:
    """Return seconds until HH:MM, scheduling tomorrow if time has passed today."""
    try:
        target_time = datetime.strptime(clock_time, "%H:%M").time()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Waktu mesti dalam format HH:MM, contoh 23:30.") from exc

    now = datetime.now()
    target = datetime.combine(now.date(), target_time)
    if target <= now:
        target += timedelta(days=1)

    return max(1, int((target - now).total_seconds()))


def human_duration(seconds: int) -> str:
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours} jam")
    if minutes:
        parts.append(f"{minutes} minit")
    if secs or not parts:
        parts.append(f"{secs} saat")
    return " ".join(parts)


def detect_os() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "linux":
        return "linux"
    raise RuntimeError(f"Platform belum disokong: {platform.system()}")


def command_for(action: str, delay_seconds: int | None = None) -> list[str]:
    """Build the native OS command for an action."""
    os_name = detect_os()

    if action == "cancel":
        if os_name == "windows":
            return ["shutdown", "/a"]
        return ["shutdown", "-c"]

    if action == "logout":
        if os_name == "windows":
            return ["shutdown", "/l"]
        return ["loginctl", "terminate-user", getpass.getuser()]

    if action not in {"shutdown", "restart"}:
        raise ValueError(f"Tindakan tidak disokong: {action}")

    if delay_seconds is None:
        raise ValueError("delay_seconds diperlukan untuk shutdown/restart")

    if os_name == "windows":
        flag = "/s" if action == "shutdown" else "/r"
        return ["shutdown", flag, "/t", str(delay_seconds)]

    # Linux shutdown works in minutes. For delays below one minute, use now.
    linux_action = "-h" if action == "shutdown" else "-r"
    if delay_seconds < 60:
        when = "now"
    else:
        minutes = max(1, (delay_seconds + 59) // 60)
        when = f"+{minutes}"
    return ["shutdown", linux_action, when]


def run_command(command: list[str], dry_run: bool) -> int:
    printable = " ".join(command)
    if dry_run:
        print(f"[DRY-RUN] {printable}")
        return 0

    try:
        completed = subprocess.run(command, check=False)
    except FileNotFoundError:
        print(f"Ralat: arahan sistem tidak ditemui: {command[0]}", file=sys.stderr)
        return 1
    except PermissionError:
        print("Ralat: kebenaran tidak mencukupi untuk menjalankan arahan ini.", file=sys.stderr)
        return 1

    if completed.returncode != 0:
        print(
            "Arahan gagal. Pada Linux, anda mungkin memerlukan kebenaran sistem "
            "yang sesuai untuk shutdown, restart atau logout.",
            file=sys.stderr,
        )
    return completed.returncode


def wait_for_action(delay_seconds: int) -> None:
    """Wait before an action that has no portable native scheduling support."""
    time.sleep(delay_seconds)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autoshutdown",
        description="Jadualkan shutdown, restart atau logout komputer dengan mudah.",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    for action in ("shutdown", "restart", "logout"):
        sub = subparsers.add_parser(action, help=f"Jadualkan {action}")
        timing = sub.add_mutually_exclusive_group(required=True)
        timing.add_argument("--in", dest="delay", type=parse_duration, help="Contoh: 30m, 2h")
        timing.add_argument("--at", dest="at_time", help="Waktu 24 jam, contoh: 23:30")
        sub.add_argument("--dry-run", action="store_true", help="Papar arahan sahaja tanpa menjalankannya")

    cancel = subparsers.add_parser("cancel", help="Batalkan shutdown/restart berjadual")
    cancel.add_argument("--dry-run", action="store_true", help="Papar arahan sahaja tanpa menjalankannya")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "cancel":
        command = command_for("cancel")
        print("Membatalkan arahan shutdown/restart berjadual...")
        return run_command(command, args.dry_run)

    delay_seconds = args.delay if args.delay is not None else seconds_until(args.at_time)
    target = datetime.now() + timedelta(seconds=delay_seconds)

    labels = {
        "shutdown": "Shutdown",
        "restart": "Restart",
        "logout": "Logout",
    }
    verb = labels[args.action]

    print(
        f"{verb} dijadualkan dalam {human_duration(delay_seconds)} "
        f"(anggaran {target.strftime('%Y-%m-%d %H:%M:%S')})."
    )

    if args.action == "logout":
        command = command_for("logout")
        if args.dry_run:
            print(f"[DRY-RUN] Tunggu {delay_seconds} saat sebelum logout.")
            return run_command(command, True)

        try:
            wait_for_action(delay_seconds)
        except KeyboardInterrupt:
            print("\nAutoLogout dibatalkan oleh pengguna.")
            return 130
        return run_command(command, False)

    command = command_for(args.action, delay_seconds)
    return run_command(command, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
