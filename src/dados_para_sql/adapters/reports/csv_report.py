"""Saídas CSV de registros válidos e inconsistências."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

from dados_para_sql.domain.models import SanitizedRecord


def write_valid_records(records: Iterable[SanitizedRecord], output_path: Path) -> None:
    """Escreve somente registros aptos ou corrigidos."""
    fields = ["name", "cpf", "email", "phone", "address", "accepts_lgpd"]
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(record.values)


def write_error_report(records: Iterable[SanitizedRecord], output_path: Path) -> None:
    """Escreve uma linha por inconsistência para facilitar regularização."""
    fields = [
        "file_name",
        "sheet_name",
        "row_number",
        "field",
        "code",
        "severity",
        "original_value",
        "normalized_value",
        "message",
        "suggested_action",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for record in records:
            for issue in record.issues:
                field_name = _field_from_code(issue.code)
                writer.writerow(
                    {
                        "file_name": record.source.file_name,
                        "sheet_name": record.source.sheet_name or "",
                        "row_number": record.source.row_number,
                        "field": field_name,
                        "code": issue.code,
                        "severity": issue.severity,
                        "original_value": record.original_values.get(field_name, ""),
                        "normalized_value": record.values.get(field_name, ""),
                        "message": issue.message,
                        "suggested_action": issue.suggested_action,
                    }
                )


def _field_from_code(code: str) -> str:
    if code.startswith("CPF"):
        return "cpf"
    if code.startswith("EMAIL"):
        return "email"
    if code.startswith("PHONE"):
        return "phone"
    if code.startswith("ADDRESS"):
        return "address"
    if code.startswith("LGPD"):
        return "accepts_lgpd"
    return "name"
