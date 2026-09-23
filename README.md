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

## Processamento inicial funcional

```bash
dados-para-sql process \
  --input samples/input/cadastro_ficticio_malformatado.xlsx \
  --output-dir output \
  --table dbo.People \
  --sql-mode script
```

Saídas geradas:

- `valid_records.csv`: somente registros aptos ou corrigidos com segurança;
- `errors.csv`: uma linha por inconsistência, com arquivo, aba, linha, campo, valores original e tratado, motivo e ação sugerida;
- `summary.json`: contagens da execução;
- `inserts.sql`: script SQL Server revisável.

### Flags de SQL

| Flag | Valores | Efeito |
|---|---|---|
| `--sql-mode` | `none`, `script`, `execute`, `both` | Controla se gera script, executa no banco ou faz ambos. O padrão é `script`. |
| `--table` | Ex.: `dbo.People` | Tabela de destino. Aceita somente identificadores simples e é delimitada com colchetes. |
| `--sql-output` | Caminho de arquivo | Define o caminho do script gerado. |
| `--sql-batch-size` | Número inteiro | Quantidade de registros por `INSERT`. |
| `--no-transaction` | Flag | Omite o bloco `TRY/CATCH` e transação somente no arquivo de script. |
| `--database-url` | URL SQLAlchemy | Obrigatória para `execute` ou `both`. Também pode vir de `DADOS_PARA_SQL_DATABASE_URL`. |

O modo `execute` usa parâmetros e transação da conexão. Ele não executa o script literal, evitando que apóstrofos, acentos e dados da planilha virem SQL concatenado.

O script gerado usa literais `N'...'` para preservar acentuação no SQL Server e duplica apóstrofos, como `D'Ávila` → `N'D''Ávila'`.

## Massas de teste

Os arquivos `samples/input/cadastro_ficticio_malformatado.xlsx` e `samples/input/cadastro_ficticio_malformatado.xls` possuem somente dados fictícios. Eles incluem aba de distração, cabeçalho deslocado, aspas e apóstrofos em nomes, CPF formatado e sem formatação, telefones variados, e-mails inválidos, endereço vazio e aceite LGPD em vários formatos.

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
