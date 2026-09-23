"""Leitura de XLSX, XLS e CSV com identificação de cabeçalho."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CANONICAL_COLUMNS: dict[str, tuple[str, ...]] = {
    "name": ("nome", "nome completo", "name"),
    "cpf": ("cpf", "c.p.f.", "documento"),
    "email": ("email", "e-mail", "e mail"),
    "phone": ("telefone", "celular", "fone", "phone"),
    "address": ("endereco", "endereço", "logradouro", "address"),
    "accepts_lgpd": ("aceita lgpd", "aceita lgpd sim nao", "consentimento lgpd", "lgpd"),
}


@dataclass(frozen=True, slots=True)
class ReadResult:
    """Dados lidos e metadados da seleção de aba."""

    rows: list[dict[str, Any]]
    sheet_name: str | None
    header_row: int


def normalize_header(value: object) -> str:
    """Normaliza títulos exclusivamente para comparação."""
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _column_mapping(headers: list[object]) -> dict[str, int]:
    normalized_headers = [normalize_header(header) for header in headers]
    mapping: dict[str, int] = {}
    for canonical, aliases in CANONICAL_COLUMNS.items():
        alias_set = {normalize_header(alias) for alias in aliases}
        matches = [index for index, header in enumerate(normalized_headers) if header in alias_set]
        if len(matches) == 1:
            mapping[canonical] = matches[0]
    return mapping


def _require_pandas() -> Any:
    try:
        import pandas as pd
    except ImportError as error:
        raise RuntimeError(
            "Dependência pandas não instalada. Execute 'uv sync --extra dev' antes de processar arquivos."
        ) from error
    return pd


def read_input_file(file_path: Path, header_scan_limit: int = 30) -> ReadResult:
    """Lê a melhor aba encontrada e retorna registros com nomes canônicos."""
    pd = _require_pandas()
    suffix = file_path.suffix.lower()
    if suffix not in {".xlsx", ".xls", ".csv"}:
        raise ValueError(f"Formato não suportado: {suffix}")

    if suffix == ".csv":
        raw = pd.read_csv(file_path, header=None, dtype=object, keep_default_na=False)
        candidates = [(None, raw)]
    else:
        excel_file = pd.ExcelFile(file_path)
        candidates = [(sheet_name, pd.read_excel(excel_file, sheet_name=sheet_name, header=None, dtype=object)) for sheet_name in excel_file.sheet_names]

    best: tuple[str | None, int, dict[str, int], Any] | None = None
    for sheet_name, raw in candidates:
        for row_index in range(min(header_scan_limit, len(raw.index))):
            headers = raw.iloc[row_index].tolist()
            mapping = _column_mapping(headers)
            score = len(mapping)
            if best is None or score > len(best[2]):
                best = (sheet_name, row_index, mapping, raw)

    if best is None or len(best[2]) != len(CANONICAL_COLUMNS):
        raise ValueError(
            "Cabeçalho não encontrado. São necessárias as colunas Nome, CPF, E-mail, Telefone, Endereço e Aceita LGPD."
        )

    sheet_name, header_row, mapping, raw = best
    records: list[dict[str, Any]] = []
    for _, row in raw.iloc[header_row + 1 :].iterrows():
        values = row.tolist()
        if all(str(value).strip() in {"", "nan", "None"} for value in values):
            continue
        records.append({canonical: values[index] if index < len(values) else None for canonical, index in mapping.items()})
    return ReadResult(records, sheet_name, header_row + 1)
