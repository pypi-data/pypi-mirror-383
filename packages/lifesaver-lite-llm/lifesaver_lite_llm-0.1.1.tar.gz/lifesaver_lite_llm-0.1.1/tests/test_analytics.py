import unittest

from lifesaver_lite_llm.core.analytics import analyze_requests


class TestAnalytics(unittest.TestCase):
    def test_basic_stats(self):
        rows = [
            {
                "model": "claude-3-sonnet",
                "input_text": "hello world",
                "tokens_in": 5,
                "tokens_out": 10,
                "latency_ms": 100,
            },
            {
                "model": "claude-3-sonnet",
                "input_text": "hello agent",
                "tokens_in": 7,
                "tokens_out": 12,
                "latency_ms": 200,
            },
            {
                "model": "claude-3-haiku",
                "input_text": "world agent",
                "tokens_in": 3,
                "tokens_out": 6,
                "latency_ms": 300,
            },
        ]
        s = analyze_requests(rows)
        self.assertEqual(s["total"], 3)
        self.assertIn("claude-3-sonnet", s["by_model"])
        self.assertGreater(s["avg_tokens_in"], 0)
        self.assertTrue(len(s["top_tokens"]) > 0)


if __name__ == "__main__":
    unittest.main()
