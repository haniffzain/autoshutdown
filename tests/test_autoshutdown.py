import unittest
from unittest.mock import patch

import autoshutdown


class ParseDurationTests(unittest.TestCase):
    def test_seconds(self):
        self.assertEqual(autoshutdown.parse_duration("30s"), 30)

    def test_minutes(self):
        self.assertEqual(autoshutdown.parse_duration("15m"), 900)

    def test_hours(self):
        self.assertEqual(autoshutdown.parse_duration("2h"), 7200)

    def test_invalid_duration(self):
        with self.assertRaises(Exception):
            autoshutdown.parse_duration("10x")


class CommandTests(unittest.TestCase):
    @patch("autoshutdown.detect_os", return_value="windows")
    def test_windows_shutdown(self, _):
        self.assertEqual(
            autoshutdown.command_for("shutdown", 90),
            ["shutdown", "/s", "/t", "90"],
        )

    @patch("autoshutdown.detect_os", return_value="windows")
    def test_windows_restart(self, _):
        self.assertEqual(
            autoshutdown.command_for("restart", 90),
            ["shutdown", "/r", "/t", "90"],
        )

    @patch("autoshutdown.detect_os", return_value="windows")
    def test_windows_logout(self, _):
        self.assertEqual(
            autoshutdown.command_for("logout"),
            ["shutdown", "/l"],
        )

    @patch("autoshutdown.detect_os", return_value="windows")
    def test_windows_cancel(self, _):
        self.assertEqual(autoshutdown.command_for("cancel"), ["shutdown", "/a"])

    @patch("autoshutdown.detect_os", return_value="linux")
    def test_linux_shutdown_minutes_round_up(self, _):
        self.assertEqual(
            autoshutdown.command_for("shutdown", 61),
            ["shutdown", "-h", "+2"],
        )

    @patch("autoshutdown.detect_os", return_value="linux")
    def test_linux_restart_now(self, _):
        self.assertEqual(
            autoshutdown.command_for("restart", 30),
            ["shutdown", "-r", "now"],
        )

    @patch("autoshutdown.getpass.getuser", return_value="haniff")
    @patch("autoshutdown.detect_os", return_value="linux")
    def test_linux_logout(self, _, __):
        self.assertEqual(
            autoshutdown.command_for("logout"),
            ["loginctl", "terminate-user", "haniff"],
        )


if __name__ == "__main__":
    unittest.main()
