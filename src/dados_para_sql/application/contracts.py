"""Contratos entre casos de uso e infraestrutura."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Protocol

from dados_para_sql.domain.models import ProcessedRecord


class SpreadsheetReader(Protocol):
    """Lê valores brutos de um arquivo suportado."""

    def supports(self, file_path: Path) -> bool:
        """Informa se o leitor suporta o arquivo."""

    def read_rows(self, file_path: Path) -> Iterable[tuple[object, ...]]:
        """Retorna linhas brutas do arquivo."""


class ReportWriter(Protocol):
    """Gera relatórios de uma execução."""

    def write(self, records: Iterable[ProcessedRecord], output_path: Path) -> Path:
        """Gera e retorna o caminho do relatório."""

