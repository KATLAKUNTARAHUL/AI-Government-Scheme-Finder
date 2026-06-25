from __future__ import annotations

from textwrap import wrap
from typing import Any


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _format_profile_lines(profile: dict[str, Any]) -> list[str]:
    lines = ["Applicant Profile"]
    for key, value in profile.items():
        lines.append(f"{key.replace('_', ' ').title()}: {value}")
    return lines


def _format_recommendation_lines(recommendations: list[dict[str, Any]]) -> list[str]:
    lines = ["Recommended Schemes"]
    for item in recommendations:
        status = "Eligible" if item.get("eligible") else "Ineligible"
        reasons = "; ".join(item.get("reasons") or ["Strong match"])
        lines.append(f"{item.get('scheme_name')} | {status} | Score {item.get('score', 0)}")
        lines.append(f"Reason: {reasons}")
        benefits = item.get("benefits") or item.get("description") or ""
        if benefits:
            lines.append(f"Benefits: {benefits}")
    return lines


def _build_page_stream(lines: list[str]) -> bytes:
    commands = ["BT", "/F1 11 Tf", "72 770 Td"]
    first_line = True
    for line in lines:
        wrapped_lines = wrap(str(line), width=90) or [""]
        for wrapped_line in wrapped_lines:
            if first_line:
                commands.append(f"({_escape_pdf_text(wrapped_line)}) Tj")
                first_line = False
            else:
                commands.append("T*")
                commands.append(f"({_escape_pdf_text(wrapped_line)}) Tj")
    commands.append("ET")
    return "\n".join(commands).encode("latin-1")


def _build_pdf_objects(lines_by_page: list[list[str]]) -> bytes:
    objects: list[tuple[bytes, bool]] = []
    objects.append((b"<< /Type /Catalog /Pages 2 0 R >>", False))

    kid_refs = [f"{4 + index * 2} 0 R" for index in range(len(lines_by_page))]
    pages_object = f"<< /Type /Pages /Count {len(lines_by_page)} /Kids [{' '.join(kid_refs)}] >>".encode("latin-1")
    objects.append((pages_object, False))
    objects.append((b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", False))

    for page_index, lines in enumerate(lines_by_page):
        content_object_number = 5 + page_index * 2
        page_object = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_object_number} 0 R >>"
        ).encode("latin-1")
        content_stream = _build_page_stream(lines)
        objects.append((page_object, False))
        objects.append((content_stream, True))

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, (payload, is_stream) in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_number} 0 obj\n".encode("latin-1"))
        if is_stream:
            output.extend(f"<< /Length {len(payload)} >>\nstream\n".encode("latin-1"))
            output.extend(payload)
            output.extend(b"\nendstream\nendobj\n")
        else:
            output.extend(payload)
            output.extend(b"\nendobj\n")

    xref_position = len(output)
    total_objects = len(objects)
    output.extend(f"xref\n0 {total_objects + 1}\n".encode("latin-1"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    output.extend(
        (
            "trailer\n"
            f"<< /Size {total_objects + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_position}\n%%EOF"
        ).encode("latin-1")
    )
    return bytes(output)


def build_report_pdf(profile: dict[str, Any], recommendations: list[dict[str, Any]]) -> bytes:
    lines = _format_profile_lines(profile) + [""] + _format_recommendation_lines(recommendations)
    pages: list[list[str]] = []
    page_size = 30
    for start in range(0, len(lines), page_size):
        pages.append(lines[start : start + page_size])
    return _build_pdf_objects(pages)