from pathlib import Path
import unittest

from lifesaver_lite_llm.core.parser import load_requests, normalize_record


class TestParser(unittest.TestCase):
    def setUp(self):
        self.tmp = Path("examples/sample_requests.json")

    def test_load_requests(self):
        items = load_requests(self.tmp)
        self.assertGreaterEqual(len(items), 3)
        for it in items:
            self.assertIn("input_text", it)
            self.assertIn("content_hash", it)

    def test_normalize_record(self):
        rec = {
            "model": "claude-3-sonnet",
            "prompt": "Summarize: https://example.com",
            "usage": {"input_tokens": 10, "output_tokens": 20},
            "metrics": {"latency_ms": 1234},
        }
        out = normalize_record(rec)
        self.assertEqual(out["model"], "claude-3-sonnet")
        self.assertIn("Summarize", out["input_text"])
        self.assertEqual(out["tokens_in"], 10)
        self.assertEqual(out["tokens_out"], 20)
        self.assertEqual(out["latency_ms"], 1234)


if __name__ == "__main__":
    unittest.main()
