"""Offline tests for synthetic reference data and tool dispatch."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.knowledge_base import KnowledgeBase


class KnowledgeBaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kb = KnowledgeBase()

    def test_search_hospitals_by_city(self) -> None:
        self.assertEqual(self.kb.search_hospitals("Bengaluru")[0]["id"], "GC-BLR-01")

    def test_unknown_hospital_returns_no_fabricated_record(self) -> None:
        self.assertIsNone(self.kb.get_hospital_details("UNKNOWN"))

    def test_hours_are_verified_data(self) -> None:
        self.assertEqual(self.kb.get_opening_hours("GC-BLR-01", "Patient Reception")[0]["hours"], "Mon-Fri 08:00-18:00")

    def test_hospital_language_mapping(self) -> None:
        self.assertIn({"code":"kn","name":"Kannada"}, self.kb.get_supported_languages("GC-BLR-01"))

    def test_unknown_tool_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            self.kb.execute("delete_hospital", {})


if __name__ == "__main__":
    unittest.main()
