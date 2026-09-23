from dados_para_sql.adapters.database.sql_writer import build_insert_script
from dados_para_sql.domain.enums import RecordStatus
from dados_para_sql.domain.models import SanitizedRecord, SourceLocation


def test_insert_script_uses_unicode_prefix_and_escapes_apostrophe() -> None:
    record = SanitizedRecord(
        SourceLocation("test.xlsx", "Dados", 2),
        {
            "name": "D'Ávila",
            "cpf": "52998224725",
            "email": "ana@example.com",
            "phone": "11999999999",
            "address": "Rua São João, 10",
            "accepts_lgpd": "SIM",
        },
        {
            "name": "D'Ávila",
            "cpf": "52998224725",
            "email": "ana@example.com",
            "phone": "11999999999",
            "address": "Rua São João, 10",
            "accepts_lgpd": "SIM",
        },
        (),
        (),
        RecordStatus.APPROVED,
    )

    script = build_insert_script([record], "dbo.People")

    assert "BEGIN TRANSACTION;" in script
    assert "BEGIN CATCH" in script
    assert "N'D''Ávila'" in script
    assert "N'Rua São João, 10'" in script
