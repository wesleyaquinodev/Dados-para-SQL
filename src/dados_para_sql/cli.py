"""Interface de linha de comando."""

from __future__ import annotations

import argparse

from dados_para_sql import __version__


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser principal da aplicação."""
    parser = argparse.ArgumentParser(
        prog="dados-para-sql",
        description="Valida e prepara planilhas para importação segura.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main() -> None:
    """Executa a interface de linha de comando."""
    build_parser().parse_args()


if __name__ == "__main__":
    main()

