from __future__ import annotations

from typing import Any


def _normalize_text(value: Any) -> str:
	return str(value or "").strip().lower()


def _parse_int(value: Any) -> int | None:
	if value in (None, ""):
		return None
	cleaned = "".join(character for character in str(value) if character.isdigit())
	return int(cleaned) if cleaned else None


def _matches_any(candidate: str, allowed_values: list[str]) -> bool:
	if not allowed_values:
		return True

	normalized_candidate = _normalize_text(candidate)
	normalized_allowed = [_normalize_text(item) for item in allowed_values]
	if "any" in normalized_allowed:
		return True

	return any(option and option in normalized_candidate for option in normalized_allowed)


def evaluate_eligibility(profile: dict[str, Any], scheme: dict[str, Any]) -> dict[str, Any]:
	age = _parse_int(profile.get("age"))
	income = _parse_int(profile.get("income"))
	occupation = _normalize_text(profile.get("occupation"))
	state = _normalize_text(profile.get("state"))
	category = _normalize_text(profile.get("category"))

	reasons: list[str] = []
	score = 0

	min_age = _parse_int(scheme.get("age_min"))
	max_age = _parse_int(scheme.get("age_max"))
	income_max = _parse_int(scheme.get("income_max"))
	occupations = list(scheme.get("occupations") or [])
	states = list(scheme.get("states") or [])
	eligible_categories = list(scheme.get("eligible_categories") or [])

	if min_age is not None and age is not None:
		if age < min_age:
			reasons.append(f"Minimum age is {min_age}.")
		else:
			score += 1

	if max_age is not None and age is not None:
		if age > max_age:
			reasons.append(f"Maximum age is {max_age}.")
		else:
			score += 1

	if income_max is not None and income is not None:
		if income > income_max:
			reasons.append(f"Household income should be at most {income_max:,}.")
		else:
			score += 1

	if occupations and not _matches_any(occupation, occupations):
		reasons.append("Occupation does not match the scheme requirements.")
	elif occupations:
		score += 1

	if states and not _matches_any(state, states):
		reasons.append("State or region is not covered by the scheme.")
	elif states:
		score += 1

	if eligible_categories and not _matches_any(category, eligible_categories):
		reasons.append("Category does not match the scheme requirements.")
	elif eligible_categories:
		score += 1

	eligible = not reasons
	return {
		"eligible": eligible,
		"score": score,
		"reasons": reasons,
	}