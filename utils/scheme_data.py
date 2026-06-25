from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT_DIR / "data" / "schemes.csv"


DEFAULT_SCHEMES: list[dict[str, Any]] = [
    {
        "scheme_name": "PM-KISAN",
        "category": "Agriculture",
        "description": "Income support for eligible farmer families",
        "age_min": 18,
        "age_max": 65,
        "income_max": None,
        "occupations": ["Farmer", "Agriculturist"],
        "states": ["Any"],
        "eligible_categories": ["Any"],
        "benefits": "Direct annual income support for farmers",
        "link": "https://pmkisan.gov.in",
        "keywords": ["farmer", "agriculture", "income support"],
    },
    {
        "scheme_name": "PM Mudra Yojana",
        "category": "Finance",
        "description": "Collateral-free loans for micro and small businesses",
        "age_min": 18,
        "age_max": 65,
        "income_max": None,
        "occupations": ["Self-employed", "Entrepreneur", "MSME"],
        "states": ["Any"],
        "eligible_categories": ["Any"],
        "benefits": "Business loans for small enterprises",
        "link": "https://www.mudra.org.in",
        "keywords": ["micro", "loan", "business", "self employed"],
    },
    {
        "scheme_name": "National Scholarship Portal",
        "category": "Education",
        "description": "Scholarship access for eligible students across India",
        "age_min": 6,
        "age_max": 30,
        "income_max": 500000,
        "occupations": ["Student"],
        "states": ["Any"],
        "eligible_categories": ["SC", "ST", "OBC", "General", "EWS"],
        "benefits": "Scholarships for school and higher education",
        "link": "https://scholarships.gov.in",
        "keywords": ["scholarship", "education", "student"],
    },
]


def _split_field(value: str | None) -> list[str]:
    if not value:
        return []
    values = [item.strip() for item in value.replace(",", "|").split("|")]
    return [item for item in values if item]


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    cleaned = "".join(character for character in str(value) if character.isdigit())
    return int(cleaned) if cleaned else None


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "scheme_name": str(record.get("scheme_name") or record.get("name") or "Unknown Scheme").strip(),
        "category": str(record.get("category") or "General").strip(),
        "description": str(record.get("description") or "").strip(),
        "age_min": _parse_int(record.get("age_min")),
        "age_max": _parse_int(record.get("age_max")),
        "income_max": _parse_int(record.get("income_max")),
        "occupations": _split_field(str(record.get("occupations") or "Any")),
        "states": _split_field(str(record.get("states") or "Any")),
        "eligible_categories": _split_field(str(record.get("eligible_categories") or "Any")),
        "benefits": str(record.get("benefits") or "").strip(),
        "link": str(record.get("link") or "").strip(),
        "keywords": _split_field(str(record.get("keywords") or "")),
    }


def load_schemes() -> list[dict[str, Any]]:
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        return DEFAULT_SCHEMES.copy()

    schemes: list[dict[str, Any]] = []
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalized = _normalize_record(row)
            if normalized["scheme_name"]:
                schemes.append(normalized)

    return schemes or DEFAULT_SCHEMES.copy()


def load_scheme_names() -> list[str]:
    return [scheme["scheme_name"] for scheme in load_schemes()]