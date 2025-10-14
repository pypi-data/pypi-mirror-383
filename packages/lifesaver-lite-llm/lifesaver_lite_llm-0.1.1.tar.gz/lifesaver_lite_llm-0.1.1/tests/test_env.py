import os
import unittest
from pathlib import Path

from lifesaver_lite_llm.core.env import load_dotenv, missing_env


class TestEnv(unittest.TestCase):
    def test_parse_and_missing(self):
        tmp = Path(".env.test")
        tmp.write_text('FOO=bar\n# comment\nQUOTED="baz qux"\n', encoding="utf-8")
        try:
            os.environ.pop("FOO", None)
            os.environ.pop("QUOTED", None)
            loaded = load_dotenv(tmp)
            self.assertEqual(loaded.get("FOO"), "bar")
            self.assertEqual(os.environ.get("QUOTED"), "baz qux")
            miss = missing_env(["FOO", "NOPE"])
            self.assertIn("NOPE", miss)
            self.assertNotIn("FOO", miss)
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
