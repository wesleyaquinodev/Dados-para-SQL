"""Geração de INSERTs SQL Server e execução parametrizada opcional."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

from dados_para_sql.domain.models import SanitizedRecord

INSERT_COLUMNS = ("name", "cpf", "email", "phone", "address", "accepts_lgpd")


def quote_identifier(identifier: str) -> str:
    """Valida e delimita identificador SQL Server sem aceitar SQL arbitrário."""
    parts = identifier.split(".")
    if not 1 <= len(parts) <= 3 or any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part) for part in parts):
        raise ValueError("Tabela deve usar identificadores simples, por exemplo dbo.Customers.")
    return ".".join(f"[{part}]" for part in parts)


def quote_nvarchar(value: str) -> str:
    """Gera literal Unicode seguro para SQL Server."""
    return "N'" + value.replace("'", "''") + "'"


def build_insert_script(
    records: Sequence[SanitizedRecord],
    table_name: str,
    batch_size: int = 500,
    include_transaction: bool = True,
) -> str:
    """Gera script SQL revisável; não exige conexão com o banco."""
    if batch_size < 1:
        raise ValueError("batch_size deve ser maior que zero.")
    table = quote_identifier(table_name)
    columns = ", ".join(quote_identifier(column) for column in INSERT_COLUMNS)
    commands: list[str] = []
    for index in range(0, len(records), batch_size):
        batch = records[index : index + batch_size]
        values = ",\n        ".join(
            "(" + ", ".join(quote_nvarchar(record.values[column]) for column in INSERT_COLUMNS) + ")"
            for record in batch
        )
        commands.append(f"    INSERT INTO {table} ({columns})\n    VALUES\n        {values};")
    inserts = "\n\n".join(commands) or "    -- Nenhum registro válido para inserir."
    if not include_transaction:
        return inserts + "\n"
    return (
        "SET XACT_ABORT ON;\n\n"
        "BEGIN TRY\n"
        "    -- Início da transação\n"
        "    BEGIN TRANSACTION;\n\n"
        f"{inserts}\n\n"
        "    -- Se tudo ocorreu bem, commit da transação\n"
        "    COMMIT;\n\n"
        "END TRY\n"
        "BEGIN CATCH\n"
        "    -- Em caso de erro, rollback\n"
        "    IF @@TRANCOUNT > 0\n"
        "        ROLLBACK;\n\n"
        "    -- Tratamento do erro\n"
        "    PRINT ERROR_MESSAGE();\n"
        "    THROW;\n"
        "END CATCH;\n"
    )


def execute_records(records: Iterable[SanitizedRecord], table_name: str, database_url: str) -> int:
    """Executa INSERT parametrizado em transação. Nunca usa o script literal para executar."""
    try:
        from sqlalchemy import create_engine, text
    except ImportError as error:
        raise RuntimeError("SQLAlchemy não instalado. Execute 'uv sync --extra sqlserver'.") from error

    safe_table = quote_identifier(table_name)
    columns = ", ".join(quote_identifier(column) for column in INSERT_COLUMNS)
    parameters = ", ".join(f":{column}" for column in INSERT_COLUMNS)
    statement = text(f"INSERT INTO {safe_table} ({columns}) VALUES ({parameters})")
    payload = [{column: record.values[column] for column in INSERT_COLUMNS} for record in records]
    if not payload:
        return 0
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(statement, payload)
    return len(payload)
