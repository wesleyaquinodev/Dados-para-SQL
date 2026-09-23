"""Modelos imutáveis usados durante a validação."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dados_para_sql.domain.enums import IssueSeverity, RecordStatus


@dataclass(frozen=True, slots=True)
class SourceLocation:
    """Localização original de uma linha em um arquivo de entrada."""

    file_name: str
    sheet_name: str | None
    row_number: int


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Inconsistência encontrada no valor de um campo."""

    code: str
    severity: IssueSeverity
    message: str
    suggested_action: str


@dataclass(frozen=True, slots=True)
class FieldValue:
    """Valor original, normalizado e auditável de um campo."""

    field_name: str
    original_value: Any
    original_type: str
    normalized_value: Any | None
    transformations: tuple[str, ...] = ()
    issues: tuple[ValidationIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class ProcessedRecord:
    """Registro processado sem apagar a origem ou as inconsistências."""

    source: SourceLocation
    fields: tuple[FieldValue, ...]
    status: RecordStatus
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)

