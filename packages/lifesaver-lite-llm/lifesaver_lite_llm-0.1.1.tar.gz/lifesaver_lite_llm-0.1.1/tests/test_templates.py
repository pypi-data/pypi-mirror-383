import unittest

from lifesaver_lite_llm.core.templates import normalize_prompt, extract_templates


class TestTemplates(unittest.TestCase):
    def test_normalize_prompt(self):
        p = "Fetch https://example.com at 2024-10-10"
        n = normalize_prompt(p)
        self.assertIn("<URL>", n)
        self.assertIn("<DATE>", n)

    def test_extract_templates(self):
        prompts = [
            "Summarize https://a.com",
            "Summarize https://b.com",
            "Translate 123 words",
            "Translate 456 words",
            "Other task",
        ]
        temps = extract_templates(prompts, min_support=2)
        # Should detect at least two templates
        self.assertGreaterEqual(len(temps), 2)


if __name__ == "__main__":
    unittest.main()
