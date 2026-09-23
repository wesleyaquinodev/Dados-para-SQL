"""Enums do domínio."""

from enum import StrEnum


class IssueSeverity(StrEnum):
    """Severidade de uma inconsistência."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class RecordStatus(StrEnum):
    """Resultado do processamento de um registro."""

    APPROVED = "APPROVED"
    CORRECTED = "CORRECTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"

