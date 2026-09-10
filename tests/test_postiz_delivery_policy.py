import unittest
from datetime import datetime, timedelta, timezone

from scripts.postiz_delivery_policy import delivery_error_is_terminal, rate_limit_decision


class PostizDeliveryPolicyTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)
        self.limits = {
            "minIntervalSeconds": 900,
            "hourlyLimit": 4,
            "dailyLimit": 24,
            "errorGraceMinutes": 60,
        }

    def package(self, minutes_ago, status="published", postiz_id="task"):
        return {
            "id": f"pkg-{minutes_ago}",
            "status": status,
            "postizPostId": postiz_id,
            "postizSubmissionAt": (self.now - timedelta(minutes=minutes_ago)).isoformat(),
        }

    def test_allows_first_submission(self):
        self.assertTrue(rate_limit_decision({"packages": []}, at=self.now, limits=self.limits)["allowed"])

    def test_blocks_inside_minimum_interval(self):
        decision = rate_limit_decision({"packages": [self.package(10)]}, at=self.now, limits=self.limits)
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "minimum_interval")

    def test_allows_at_minimum_interval_boundary(self):
        self.assertTrue(rate_limit_decision({"packages": [self.package(15)]}, at=self.now, limits=self.limits)["allowed"])

    def test_blocks_four_submissions_in_previous_hour(self):
        packages = [self.package(minutes) for minutes in (16, 25, 40, 55)]
        decision = rate_limit_decision({"packages": packages}, at=self.now, limits=self.limits)
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "hourly_limit")

    def test_blocks_twenty_four_submissions_in_previous_day(self):
        packages = [self.package(16 + index * 40) for index in range(24)]
        decision = rate_limit_decision({"packages": packages}, at=self.now, limits=self.limits)
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "daily_limit")

    def test_blocks_unresolved_accepted_delivery(self):
        decision = rate_limit_decision(
            {"packages": [self.package(20, status="publishing")]}, at=self.now, limits=self.limits
        )
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "pending_delivery_reconciliation")

    def test_error_is_not_terminal_during_delayed_success_grace(self):
        self.assertFalse(delivery_error_is_terminal(self.package(20, status="publishing"), at=self.now))
        self.assertTrue(delivery_error_is_terminal(self.package(61, status="publishing"), at=self.now))


if __name__ == "__main__":
    unittest.main()
