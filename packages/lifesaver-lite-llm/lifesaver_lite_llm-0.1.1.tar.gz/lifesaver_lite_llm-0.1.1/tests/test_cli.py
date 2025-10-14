from pathlib import Path
import unittest

from lifesaver_lite_llm.cli import main


class TestCLI(unittest.TestCase):
    def test_ingest_and_analyze(self):
        db = Path("data/test_analysis.db")
        try:
            if db.exists():
                db.unlink()
        except Exception:
            pass
        rc = main(
            ["--db", str(db), "ingest", "--input", "examples/sample_requests.json"]
        )
        self.assertEqual(rc, 0)
        out = Path("reports/test_report.md")
        if out.exists():
            out.unlink()
        rc = main(["--db", str(db), "analyze", "--out", str(out)])
        self.assertEqual(rc, 0)
        self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
