"""Interface de linha de comando."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dados_para_sql import __version__
from dados_para_sql.application.process_file import process_file


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser principal da aplicação."""
    parser = argparse.ArgumentParser(
        prog="dados-para-sql",
        description="Valida e prepara planilhas para importação segura.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command")
    process_parser = subparsers.add_parser("process", help="Sanitiza uma planilha e gera as saídas.")
    process_parser.add_argument("--input", required=True, type=Path, help="Arquivo .xlsx, .xls ou .csv.")
    process_parser.add_argument("--output-dir", type=Path, default=Path("output"))
    process_parser.add_argument("--table", default="dbo.People", help="Tabela SQL de destino.")
    process_parser.add_argument(
        "--sql-mode",
        choices=("none", "script", "execute", "both"),
        default="script",
        help="script gera SQL; execute grava parametrizado; both faz os dois.",
    )
    process_parser.add_argument("--sql-output", type=Path, default=None)
    process_parser.add_argument("--sql-batch-size", type=int, default=500)
    process_parser.add_argument("--no-transaction", action="store_true")
    process_parser.add_argument("--database-url", default=None)
    return parser


def main() -> None:
    """Executa a interface de linha de comando."""
    arguments = build_parser().parse_args()
    if arguments.command != "process":
        return
    database_url = arguments.database_url or os.getenv("DADOS_PARA_SQL_DATABASE_URL")
    summary = process_file(
        input_file=arguments.input,
        output_dir=arguments.output_dir,
        table_name=arguments.table,
        sql_mode=arguments.sql_mode,
        sql_output=arguments.sql_output,
        batch_size=arguments.sql_batch_size,
        include_transaction=not arguments.no_transaction,
        database_url=database_url,
    )
    print(
        "Processamento concluído: "
        f"{summary['valid_records']} válidos, {summary['blocked_records']} bloqueados."
    )


if __name__ == "__main__":
    main()
