import unittest
from pathlib import Path

from lifesaver_lite_llm.cli import main


class TestDashboardAndAgent(unittest.TestCase):
    def setUp(self):
        # Ensure DB has data
        db = Path("data/test_dash.db")
        if db.exists():
            db.unlink()
        rc = main(
            ["--db", str(db), "ingest", "--input", "examples/sample_requests.json"]
        )
        self.assertEqual(rc, 0)
        self.db = db

    def test_dashboard(self):
        rc = main(
            ["--db", str(self.db), "dashboard", "--providers", "configs/providers.json"]
        )
        self.assertEqual(rc, 0)

    def test_agent_plan_and_run(self):
        # plan
        rc = main(
            [
                "agent",
                "--task",
                "summarize this text",
                "--mode",
                "plan",
                "--providers",
                "configs/providers.json",
            ]
        )
        self.assertEqual(rc, 0)
        # run
        rc = main(
            [
                "agent",
                "--task",
                "write unit tests for a module",
                "--mode",
                "run",
                "--providers",
                "configs/providers.json",
            ]
        )
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
