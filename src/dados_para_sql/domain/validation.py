"""Normalização e validação de dados pessoais fictícios de entrada."""

from __future__ import annotations

import math
import re
import unicodedata
from collections.abc import Mapping
from typing import Any

from dados_para_sql.domain.enums import IssueSeverity, RecordStatus
from dados_para_sql.domain.models import SanitizedRecord, SourceLocation, ValidationIssue

REQUIRED_COLUMNS = ("name", "cpf", "email", "phone", "address", "accepts_lgpd")


def _is_blank(value: object) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value)) or str(value).strip() == ""


def _text(value: object) -> str:
    if _is_blank(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _issue(code: str, message: str, action: str) -> ValidationIssue:
    return ValidationIssue(code, IssueSeverity.ERROR, message, action)


def _collapse_spaces(value: str) -> str:
    return " ".join(value.replace("\n", " ").replace("\r", " ").split())


def _cpf_is_valid(cpf: str) -> bool:
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    first_sum = sum(int(digit) * weight for digit, weight in zip(cpf[:9], range(10, 1, -1), strict=True))
    first_digit = (first_sum * 10 % 11) % 10
    second_sum = sum(int(digit) * weight for digit, weight in zip(cpf[:10], range(11, 1, -1), strict=True))
    second_digit = (second_sum * 10 % 11) % 10
    return cpf[-2:] == f"{first_digit}{second_digit}"


def sanitize_name(value: object) -> tuple[str, tuple[str, ...], ValidationIssue | None]:
    """Normaliza espaçamento e aspas de encapsulamento sem apagar apóstrofos internos."""
    original = _text(value)
    cleaned = _collapse_spaces(
        original.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    )
    transformations: list[str] = []
    if cleaned != original:
        transformations.append("NORMALIZED_WHITESPACE_OR_QUOTES")
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {"'", '"'}:
        cleaned = cleaned[1:-1].strip()
        transformations.append("REMOVED_WRAPPING_QUOTE")
    if len(cleaned) < 2 or not any(character.isalpha() for character in cleaned):
        return cleaned, tuple(transformations), _issue(
            "NAME_INVALID",
            "Nome vazio, curto demais ou sem caracteres alfabéticos.",
            "Informe um nome com ao menos dois caracteres e letras.",
        )
    return cleaned, tuple(transformations), None


def sanitize_cpf(value: object) -> tuple[str, tuple[str, ...], ValidationIssue | None]:
    """Converte CPF em texto de 11 dígitos, com recuperação controlada de um zero."""
    original = _text(value).strip()
    if not original:
        return "", (), _issue("CPF_EMPTY", "CPF obrigatório não informado.", "Informe o CPF.")
    if re.search(r"[A-Za-z]", original):
        return "", (), _issue("CPF_INVALID_CHARACTERS", "CPF contém letras.", "Remova letras do CPF.")
    digits = re.sub(r"[^0-9]", "", original)
    transformations: list[str] = []
    if digits != original:
        transformations.append("REMOVED_CPF_FORMATTING")
    if len(digits) == 10:
        candidate = f"0{digits}"
        if _cpf_is_valid(candidate):
            return candidate, tuple(transformations + ["RECOMPOSED_LEADING_ZERO"]), None
    if len(digits) != 11:
        return digits, tuple(transformations), _issue(
            "CPF_INVALID_LENGTH",
            "CPF deve conter 11 dígitos.",
            "Corrija o CPF na planilha; zeros não são completados automaticamente.",
        )
    if not _cpf_is_valid(digits):
        return digits, tuple(transformations), _issue(
            "CPF_INVALID_CHECK_DIGITS",
            "CPF possui dígitos verificadores inválidos.",
            "Confira o CPF na planilha.",
        )
    return digits, tuple(transformations), None


def sanitize_email(value: object) -> tuple[str, tuple[str, ...], ValidationIssue | None]:
    original = _text(value)
    cleaned = original.strip().lower()
    transformations = ("TRIMMED_EMAIL",) if cleaned != original else ()
    email_pattern = r"^[^\s@]+@[^\s@.][^\s@]*\.[^\s@.]+$"
    if not re.fullmatch(email_pattern, cleaned) or ".." in cleaned:
        return cleaned, transformations, _issue(
            "EMAIL_INVALID",
            "E-mail possui formato inválido.",
            "Informe um endereço no formato nome@dominio.com.",
        )
    return cleaned, transformations, None


def sanitize_phone(value: object) -> tuple[str, tuple[str, ...], ValidationIssue | None]:
    original = _text(value)
    digits = re.sub(r"\D", "", original)
    transformations: list[str] = []
    if digits != original:
        transformations.append("REMOVED_PHONE_FORMATTING")
    if len(digits) in (12, 13) and digits.startswith("55"):
        digits = digits[2:]
        transformations.append("REMOVED_COUNTRY_CODE")
    if len(digits) not in (10, 11):
        return digits, tuple(transformations), _issue(
            "PHONE_INVALID",
            "Telefone deve conter 10 ou 11 dígitos brasileiros.",
            "Informe DDD e número do telefone.",
        )
    return digits, tuple(transformations), None


def sanitize_address(value: object) -> tuple[str, tuple[str, ...], ValidationIssue | None]:
    original = _text(value)
    cleaned = _collapse_spaces(original)
    transformations = ("NORMALIZED_ADDRESS_WHITESPACE",) if cleaned != original else ()
    if len(cleaned) < 5:
        return cleaned, transformations, _issue(
            "ADDRESS_INVALID",
            "Endereço não informado ou muito curto.",
            "Informe rua, número ou referência suficiente.",
        )
    return cleaned, transformations, None


def sanitize_lgpd(value: object) -> tuple[str, tuple[str, ...], ValidationIssue | None]:
    original = _text(value)
    cleaned = unicodedata.normalize("NFKD", original).encode("ascii", "ignore").decode().strip().upper()
    if cleaned in {"SIM", "S", "YES", "Y", "TRUE", "1"}:
        return "SIM", ("NORMALIZED_LGPD_FLAG",) if original != "SIM" else (), None
    if cleaned in {"NAO", "N", "NO", "FALSE", "0"}:
        return "NÃO", ("NORMALIZED_LGPD_FLAG",) if original != "NÃO" else (), _issue(
            "LGPD_NOT_ACCEPTED",
            "Registro sem aceite LGPD não pode ser incluído.",
            "Obtenha o aceite LGPD ou remova o registro da importação.",
        )
    return cleaned, (), _issue(
        "LGPD_INVALID",
        "Aceite LGPD deve ser SIM ou NÃO.",
        "Preencha Aceita LGPD com SIM ou NÃO.",
    )


def sanitize_record(raw_record: Mapping[str, Any], source: SourceLocation) -> SanitizedRecord:
    """Sanitiza uma linha e mantém todas as inconsistências para o relatório."""
    handlers = {
        "name": sanitize_name,
        "cpf": sanitize_cpf,
        "email": sanitize_email,
        "phone": sanitize_phone,
        "address": sanitize_address,
        "accepts_lgpd": sanitize_lgpd,
    }
    values: dict[str, str] = {}
    original_values: dict[str, str] = {}
    transformations: list[str] = []
    issues: list[ValidationIssue] = []
    for field_name in REQUIRED_COLUMNS:
        original_values[field_name] = _text(raw_record.get(field_name))
        value, field_transformations, issue = handlers[field_name](raw_record.get(field_name))
        values[field_name] = value
        transformations.extend(f"{field_name}:{item}" for item in field_transformations)
        if issue is not None:
            issues.append(issue)
    status = RecordStatus.BLOCKED if issues else (
        RecordStatus.CORRECTED if transformations else RecordStatus.APPROVED
    )
    return SanitizedRecord(source, original_values, values, tuple(transformations), tuple(issues), status)
