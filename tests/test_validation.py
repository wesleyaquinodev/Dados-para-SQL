from dados_para_sql.domain.enums import RecordStatus
from dados_para_sql.domain.models import SourceLocation
from dados_para_sql.domain.validation import sanitize_cpf, sanitize_name, sanitize_record


def test_cpf_with_formatting_is_normalized() -> None:
    cpf, transformations, issue = sanitize_cpf("529.982.247-25")

    assert cpf == "52998224725"
    assert transformations == ("REMOVED_CPF_FORMATTING",)
    assert issue is None


def test_name_with_wrapping_quote_keeps_internal_apostrophe() -> None:
    name, transformations, issue = sanitize_name('"Ana D\'Ávila"')

    assert name == "Ana D'Ávila"
    assert "REMOVED_WRAPPING_QUOTE" in transformations
    assert issue is None


def test_lgpd_no_blocks_record() -> None:
    record = sanitize_record(
        {
            "name": "Ana Silva",
            "cpf": "52998224725",
            "email": "ana@example.com",
            "phone": "(11) 99999-9999",
            "address": "Rua das Flores, 10",
            "accepts_lgpd": "Não",
        },
        SourceLocation("test.xlsx", "Dados", 2),
    )

    assert record.status is RecordStatus.BLOCKED
    assert record.issues[0].code == "LGPD_NOT_ACCEPTED"
