# Dados para SQL

Ferramenta Python para ler planilhas, identificar a aba e o cabeçalho corretos, tratar dados com segurança, apontar inconsistências e preparar registros válidos para importação em banco de dados.

## O problema que resolve

Arquivos Excel e CSV podem conter cabeçalhos fora da primeira linha, abas com nomes variados, CPFs sem zeros iniciais, e-mails inválidos, aspas em textos, duplicidades e outros problemas que tornam uma importação perigosa.

O Dados para SQL preserva o valor original, aplica apenas tratamentos seguros e registra tudo o que foi corrigido, bloqueado ou enviado para revisão.

## Princípios

- CPF e outros identificadores são tratados como texto.
- O arquivo original nunca é alterado.
- Dados ambíguos não são corrigidos automaticamente.
- Registros bloqueados não seguem para a importação.
- Banco, esquema e objeto de destino são configuráveis e explícitos.
- O modo de validação não grava no banco.

## Arquitetura

```text
interfaces/   CLI
application/  Casos de uso
domain/       Regras e modelos independentes
ports/        Contratos com leitores, bancos e relatórios
adapters/     Excel, CSV, SQL e geração de arquivos
```

## Estrutura inicial

```text
src/dados_para_sql/
  application/
  domain/
  ports/
  adapters/
tests/
configs/
docs/adr/
```

## Pré-requisitos

- Python 3.12
- [uv](https://docs.astral.sh/uv/) para criar ambiente e travar dependências

## Primeiros comandos

```bash
uv sync --extra dev
uv run dados-para-sql --version
uv run pytest
uv run ruff check .
```

## Comandos previstos

```bash
dados-para-sql validate --profile cargo_update --input ./input --output ./output
dados-para-sql dry-run --profile cargo_update --input ./input
dados-para-sql import --profile cargo_update --input ./input --approved-execution-id <uuid>
```

Por enquanto, somente `--version` está implementado. Os demais comandos serão entregues por etapas, com testes antes de liberar acesso de escrita ao banco.

## Versionamento

- Aplicação: Semantic Versioning.
- Commits: Conventional Commits.
- Dependências: `pyproject.toml` define compatibilidade e `uv.lock` registra versões exatas.
- Perfis: possuem versão própria e são registrados em cada execução.

## Segurança

- Nunca versionar `.env`, arquivos de entrada ou relatórios com dados pessoais.
- Não colocar credenciais, nomes de ambientes internos ou dados reais neste repositório.
- Usar consultas parametrizadas, transações e modo de simulação antes de importar.

## Próxima etapa

Implementar os leitores de `.xlsx`, `.xls` e `.csv` com testes para preservar valores originais e identificar a aba correta.

