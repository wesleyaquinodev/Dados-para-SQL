"""Caso de uso de processamento de um arquivo."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from dados_para_sql.adapters.database.sql_writer import build_insert_script, execute_records
from dados_para_sql.adapters.files.tabular_reader import read_input_file
from dados_para_sql.adapters.reports.csv_report import write_error_report, write_valid_records
from dados_para_sql.domain.enums import RecordStatus
from dados_para_sql.domain.models import SanitizedRecord, SourceLocation
from dados_para_sql.domain.validation import sanitize_record


def process_file(
    input_file: Path,
    output_dir: Path,
    table_name: str,
    sql_mode: str,
    sql_output: Path | None,
    batch_size: int,
    include_transaction: bool,
    database_url: str | None,
) -> dict[str, object]:
    """Lê, sanitiza e materializa as saídas de uma importação."""
    read_result = read_input_file(input_file)
    records: list[SanitizedRecord] = []
    for offset, raw_record in enumerate(read_result.rows, start=read_result.header_row + 1):
        source = SourceLocation(input_file.name, read_result.sheet_name, offset)
        records.append(sanitize_record(raw_record, source))

    valid_records = [
        record for record in records if record.status in {RecordStatus.APPROVED, RecordStatus.CORRECTED}
    ]
    invalid_records = [record for record in records if record.status is RecordStatus.BLOCKED]
    output_dir.mkdir(parents=True, exist_ok=True)
    write_valid_records(valid_records, output_dir / "valid_records.csv")
    write_error_report(invalid_records, output_dir / "errors.csv")

    generated_sql_path: Path | None = None
    if sql_mode in {"script", "both"}:
        generated_sql_path = sql_output or output_dir / "inserts.sql"
        generated_sql_path.write_text(
            build_insert_script(valid_records, table_name, batch_size, include_transaction),
            encoding="utf-8",
        )
    inserted_count = 0
    if sql_mode in {"execute", "both"}:
        if not database_url:
            raise ValueError("--database-url é obrigatório para sql-mode execute ou both.")
        inserted_count = execute_records(valid_records, table_name, database_url)

    summary = {
        "input_file": input_file.name,
        "sheet_name": read_result.sheet_name,
        "header_row": read_result.header_row,
        "total_rows": len(records),
        "valid_records": len(valid_records),
        "blocked_records": len(invalid_records),
        "sql_mode": sql_mode,
        "sql_output": str(generated_sql_path) if generated_sql_path else None,
        "inserted_count": inserted_count,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
