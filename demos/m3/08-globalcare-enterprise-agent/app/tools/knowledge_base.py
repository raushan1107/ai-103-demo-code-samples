"""Search fictional GlobalCare reference data; this module is the factual source of truth."""

import json
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parents[2] / "data"


def _load(name: str) -> list[dict[str, Any]]:
    with (DATA / name).open(encoding="utf-8") as stream:
        return json.load(stream)


class KnowledgeBase:
    """Read-only access to synthetic hospital information."""

    def __init__(self) -> None:
        self.hospitals = _load("hospitals.json")
        self.departments = _load("departments.json")
        self.services = _load("services.json")
        self.faqs = _load("faqs.json")
        self.languages = _load("supported_languages.json")

    def search_hospitals(self, query: str) -> list[dict[str, Any]]:
        terms = query.casefold().split()
        ranked = [
            (sum(term in json.dumps(h, ensure_ascii=False).casefold() for term in terms), h)
            for h in self.hospitals
        ]
        best = max((score for score, _ in ranked), default=0)
        return [hospital for score, hospital in ranked if score == best and score > 0]

    def get_hospital_details(self, hospital_id: str) -> dict[str, Any] | None:
        return next((h for h in self.hospitals if h["id"] == hospital_id), None)

    def get_department_information(self, hospital_id: str, name: str) -> list[dict[str, Any]]:
        return [d for d in self.departments if d["hospital_id"] == hospital_id and name.casefold() in d["name"].casefold()]

    def get_opening_hours(self, hospital_id: str, department: str = "") -> list[dict[str, str]]:
        return [{"department": d["name"], "hours": d["hours"]} for d in self.departments if d["hospital_id"] == hospital_id and (not department or department.casefold() in d["name"].casefold())]

    def get_supported_languages(self, hospital_id: str) -> list[dict[str, str]]:
        hospital = self.get_hospital_details(hospital_id)
        if not hospital:
            return []
        names = {entry["code"]: entry["name"] for entry in self.languages}
        return [{"code": code, "name": names.get(code, code)} for code in hospital["languages"]]

    def search_faq(self, query: str) -> list[dict[str, Any]]:
        terms = query.casefold().split()
        return [faq for faq in self.faqs if any(term in json.dumps(faq, ensure_ascii=False).casefold() for term in terms)]

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        """Dispatch a known tool; unknown tool names fail closed."""
        allowed = {
            "search_hospitals": self.search_hospitals,
            "get_hospital_details": self.get_hospital_details,
            "get_department_information": self.get_department_information,
            "get_opening_hours": self.get_opening_hours,
            "get_supported_languages": self.get_supported_languages,
            "search_faq": self.search_faq,
        }
        if name not in allowed:
            raise ValueError(f"Unknown knowledge-base tool: {name}")
        return allowed[name](**arguments)
