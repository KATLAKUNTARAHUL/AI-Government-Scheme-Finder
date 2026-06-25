from __future__ import annotations

from typing import Any

from utils.eligibility_checker import evaluate_eligibility


def _normalize_text(value: Any) -> str:
	return str(value or "").strip().lower()


def _count_keyword_hits(profile_text: str, keywords: list[str]) -> int:
	hits = 0
	for keyword in keywords:
		normalized = _normalize_text(keyword)
		if normalized and normalized in profile_text:
			hits += 1
	return hits


def rank_schemes(profile: dict[str, Any], schemes: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
	profile_text = " ".join(
		[
			str(profile.get("occupation") or ""),
			str(profile.get("state") or ""),
			str(profile.get("category") or ""),
			str(profile.get("interests") or ""),
		]
	).lower()

	ranked: list[dict[str, Any]] = []
	for scheme in schemes:
		eligibility = evaluate_eligibility(profile, scheme)
		keyword_hits = _count_keyword_hits(profile_text, list(scheme.get("keywords") or []))
		description_text = " ".join(
			[
				str(scheme.get("scheme_name") or ""),
				str(scheme.get("category") or ""),
				str(scheme.get("description") or ""),
				str(scheme.get("benefits") or ""),
			]
		).lower()
		text_hits = sum(1 for term in [profile.get("occupation"), profile.get("state"), profile.get("category")] if _normalize_text(term) and _normalize_text(term) in description_text)

		score = eligibility["score"] * 10 + keyword_hits * 3 + text_hits * 2
		if eligibility["eligible"]:
			score += 25

		ranked.append(
			{
				**scheme,
				**eligibility,
				"keyword_hits": keyword_hits,
				"score": score,
			}
		)

	ranked.sort(key=lambda item: (item["eligible"], item["score"]), reverse=True)
	return ranked[:limit]
