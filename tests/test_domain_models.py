"""Testes dos modelos de domínio."""

from dados_para_sql.domain.enums import IssueSeverity, RecordStatus
from dados_para_sql.domain.models import FieldValue, ProcessedRecord, SourceLocation, ValidationIssue


def test_processed_record_preserves_source_and_original_value() -> None:
    issue = ValidationIssue(
        code="CPF_DIGITO_INVALIDO",
        severity=IssueSeverity.ERROR,
        message="CPF inválido.",
        suggested_action="Corrija o CPF na origem.",
    )
    field = FieldValue(
        field_name="cpf",
        original_value="123.456.789-00",
        original_type="str",
        normalized_value="12345678900",
        issues=(issue,),
    )
    record = ProcessedRecord(
        source=SourceLocation(file_name="entrada.xlsx", sheet_name="Dados", row_number=7),
        fields=(field,),
        status=RecordStatus.BLOCKED,
        issues=(issue,),
    )

    assert record.source.row_number == 7
    assert record.fields[0].original_value == "123.456.789-00"
    assert record.status is RecordStatus.BLOCKED

