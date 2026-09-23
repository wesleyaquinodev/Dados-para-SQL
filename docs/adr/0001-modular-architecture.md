# ADR 0001: Arquitetura modular com portas e adaptadores

## Status

Aceita em 2026-09-23.

## Contexto

O sistema precisa aceitar vários formatos de arquivo, perfis de importação e bancos de dados sem repetir as regras de validação.

## Decisão

Separar domínio, casos de uso, contratos e adaptadores. Dependências externas ficam nos adaptadores.

## Consequências

- Novos leitores e bancos podem ser adicionados sem alterar validadores.
- Regras de negócio podem ser testadas sem Excel ou SQL Server.
- Há mais arquivos e contratos, mas cada módulo tem responsabilidade explícita.

