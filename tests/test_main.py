import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.main import build, demo_result, summarize_with_gemini, validate_result

class SummarizerTest(unittest.TestCase):
    def test_demo_result_schema(self):
        self.assertEqual(len(validate_result(demo_result())["key_points"]), 3)

    def test_invalid_result_rejected(self):
        with self.assertRaises(ValueError):
            validate_result({"headline": "只有標題"})

    def test_demo_build(self):
        with tempfile.TemporaryDirectory() as temp:
            inp = Path(temp) / "source.txt"
            out = Path(temp) / "result.json"
            inp.write_text("課堂測試文章", encoding="utf-8")
            result = build("demo", inp, out)
            self.assertTrue(out.exists())
            self.assertEqual(result["mode"], "demo")

    def test_missing_key(self):
        with self.assertRaises(ValueError):
            summarize_with_gemini("測試", "", "gemini-2.5-flash")

if __name__ == "__main__":
    unittest.main()
