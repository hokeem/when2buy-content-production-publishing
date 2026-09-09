import unittest
from datetime import datetime, timedelta, timezone

from scripts.freshness_policy import expire_stale_packages, freshness


class FreshnessPolicyTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 9, 8, 0, tzinfo=timezone.utc)

    def test_source_inside_ttl_is_eligible(self):
        result = freshness(self.now - timedelta(minutes=89), at=self.now, ttl_minutes=90)
        self.assertTrue(result["eligible"])
        self.assertEqual(result["reason"], "fresh")

    def test_source_past_ttl_is_rejected(self):
        result = freshness(self.now - timedelta(minutes=91), at=self.now, ttl_minutes=90)
        self.assertFalse(result["eligible"])
        self.assertEqual(result["reason"], "source_ttl_exceeded")

    def test_missing_timestamp_is_rejected(self):
        self.assertFalse(freshness("", at=self.now, ttl_minutes=90)["eligible"])

    def test_only_unsent_stale_packages_are_expired(self):
        state = {
            "benchmarkPosts": [
                {"id": "1", "postedAt": (self.now - timedelta(minutes=91)).isoformat()},
                {"id": "2", "postedAt": (self.now - timedelta(minutes=10)).isoformat()},
            ],
            "packages": [
                {"id": "old-ready", "benchmarkPostId": "1", "status": "ready"},
                {"id": "old-published", "benchmarkPostId": "1", "status": "published"},
                {"id": "fresh-ready", "benchmarkPostId": "2", "status": "ready"},
            ],
        }
        expired = expire_stale_packages(state, at=self.now, ttl_minutes=90)
        self.assertEqual(expired, ["old-ready"])
        self.assertEqual(state["packages"][0]["status"], "expired")
        self.assertEqual(state["packages"][1]["status"], "published")
        self.assertEqual(state["packages"][2]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
