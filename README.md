Importador e Validador de Planilhas

Sistema em Python para receber, identificar, tratar, validar e preparar arquivos .xlsx, .xls e .csv para importação segura em banco de dados.

O projeto nasce de dois cenários reais:

atualização de cargo, nível, classe e situação de empregados e estagiários;

conferência de inscrição, vínculo com subevento e presença de participantes.

O sistema deve ser genérico. As particularidades de cada processo serão implementadas por perfis de importação configuráveis, sem duplicar o fluxo principal.

1. Objetivos

impedir que erros de preenchimento cheguem ao banco de dados;

preservar o valor original recebido;

aplicar apenas correções automáticas seguras e auditáveis;

validar novamente todo valor após o tratamento;

gerar um único relatório com resumo e detalhes das inconsistências;

processar vários arquivos sem perder o resultado dos arquivos válidos quando outro falhar;

permitir simulação antes de qualquer alteração no banco;

manter banco, esquema e objeto de destino explícitos;

possibilitar a inclusão de novos layouts sem alterar o núcleo da aplicação.

2. Escopo da primeira versão

Incluído

leitura de .xlsx, .xls e .csv;

processamento de um arquivo, vários arquivos ou uma pasta;

localização da aba e da linha real do cabeçalho;

normalização de títulos e valores;

validação de CPF, e-mail, nome, datas e campos configuráveis;

detecção de duplicidades;

modo validate, sem acesso de escrita ao banco;

modo import, com transação e autorização explícita;

relatório .xlsx com resumo e inconsistências;

exportação dos registros válidos para .csv e .json;

geração opcional de .sql apenas para revisão;

perfis iniciais cargo_update e event_attendance;

testes automatizados com as massas .xls e .xlsx de homologação.

Fora da primeira versão

interface web;

aplicativo desktop;

edição automática do arquivo original;

validação da existência real de uma caixa de e-mail;

correção automática de dados ambíguos;

regras específicas gravadas diretamente no núcleo da aplicação.

Itens fora do escopo só devem entrar após decisão registrada e atualização deste documento.

3. Estratégia para reduzir retrabalho

O desenvolvimento deve seguir entregas pequenas. Cada parte precisa estar testada antes de iniciar a seguinte.

Parte

Entrega

Dependência

Condição para avançar

1

Estrutura do projeto, configuração e CLI

Nenhuma

Projeto executa localmente e no pipeline

2

Leitura de .xlsx, .xls e .csv

Parte 1

Arquivos de teste são lidos sem alterar os valores originais

3

Identificação de aba, cabeçalho e colunas

Parte 2

Casos de aba incorreta e cabeçalho deslocado passam nos testes

4

Normalizadores e validadores comuns

Parte 3

CPF, e-mail, nomes, datas e textos passam nos testes unitários

5

Perfis de cargo e presença

Parte 4

Cada perfil reconhece seu layout sem lógica duplicada

6

Consolidação, deduplicação e relatório

Parte 5

Totais do resumo conciliam com os detalhes

7

Integração com banco em modo simulação

Parte 6

Comparação antes/depois sem escrita no banco

8

Importação transacional

Parte 7

Rollback, idempotência e auditoria comprovados

9

Empacotamento e documentação operacional

Parte 8

Execução reproduzível em ambiente limpo

Regras obrigatórias contra retrabalho:

Não implementar acesso de escrita ao banco antes de concluir leitura, tratamento e relatório.

Não colocar regras de cargo ou presença dentro dos leitores de Excel.

Não duplicar validação de CPF, e-mail ou data entre perfis.

Não alterar um contrato público sem ajustar testes, documentação e versão.

Toda decisão arquitetural relevante deve ser registrada em docs/adr/.

Toda correção de defeito deve incluir um teste que reproduza o problema.

Novos layouts devem ser adicionados por configuração e adaptadores, não por vários if espalhados.

O valor original nunca deve ser sobrescrito pelo valor tratado.

4. Arquitetura de software

Será usada uma arquitetura modular inspirada em Clean Architecture e Ports and Adapters. O objetivo é separar regra de negócio, leitura de arquivos, banco de dados e geração de relatórios, sem criar camadas desnecessárias.

flowchart TD
    CLI[CLI] --> APP[Casos de uso]
    APP --> DOMAIN[Domínio e validações]
    APP --> PORTS[Portas]
    FILES[Leitores XLSX XLS CSV] --> PORTS
    DATABASE[Adaptador SQL Server] --> PORTS
    REPORTS[Relatórios e exportações] --> PORTS
    CONFIG[Perfis YAML] --> APP

Camadas

domain

Contém regras puras e independentes de bibliotecas externas:

entidades e value objects;

códigos e severidades de inconsistência;

validação de CPF, e-mail, nome e datas;

políticas de correção automática;

resultado de validação;

regras de deduplicação.

O domínio não pode importar pandas, openpyxl, xlrd, SQLAlchemy ou código da CLI.

application

Orquestra os casos de uso:

descobrir e registrar arquivos;

localizar aba e cabeçalho;

mapear colunas;

tratar e validar registros;

consolidar duplicidades;

consultar dados existentes;

simular alterações;

importar registros aprovados;

gerar resultados e manifestos.

ports

Define contratos por meio de Protocol ou classes abstratas:

SpreadsheetReader;

ProfileRepository;

ImportRepository;

ReportWriter;

ExecutionLogger.

adapters

Implementa detalhes externos:

leitor .xlsx;

leitor .xls;

leitor .csv;

SQL Server;

relatório Excel;

exportação CSV e JSON;

sistema de arquivos;

logs estruturados.

interfaces

Contém a CLI. Uma futura API deve chamar os mesmos casos de uso, sem copiar regras.

5. Estrutura de diretórios

spreadsheet-importer/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── .gitignore
├── configs/
│   ├── cargo_update.yaml
│   └── event_attendance.yaml
├── docs/
│   ├── architecture.md
│   ├── operations.md
│   └── adr/
│       └── 0001-modular-architecture.md
├── samples/
│   ├── input/
│   └── expected/
├── src/
│   └── spreadsheet_importer/
│       ├── __init__.py
│       ├── cli.py
│       ├── settings.py
│       ├── domain/
│       │   ├── entities.py
│       │   ├── enums.py
│       │   ├── errors.py
│       │   ├── normalization.py
│       │   └── validation.py
│       ├── application/
│       │   ├── commands.py
│       │   ├── services.py
│       │   └── use_cases/
│       ├── ports/
│       │   ├── readers.py
│       │   ├── repositories.py
│       │   └── reports.py
│       └── adapters/
│           ├── files/
│           ├── database/
│           └── reports/
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    └── fixtures/

6. Fluxo de processamento

Criar execution_id.

Carregar e validar o perfil solicitado.

Descobrir os arquivos de entrada.

Calcular hash SHA-256 e verificar reprocessamento.

Identificar formato real do arquivo, não apenas a extensão.

Inspecionar abas e primeiras linhas.

Selecionar aba e linha do cabeçalho por pontuação.

Mapear títulos originais para nomes canônicos.

Ler registros em lotes quando o formato permitir.

Preservar valores e tipos originais.

Normalizar campos conforme o perfil.

Validar os valores tratados.

Detectar duplicidades no arquivo, no lote e, opcionalmente, no banco.

Aplicar regras específicas do perfil.

Classificar cada registro como aprovado, corrigido, pendente de revisão ou bloqueado.

Gerar resumo, relatório detalhado, arquivo de válidos e manifesto.

No modo import, exigir validação concluída e executar a persistência em transação.

Nenhuma etapa posterior pode apagar a evidência produzida pelas etapas anteriores.

7. Modelo de dados interno

Cada célula processada deve possuir, no mínimo:

@dataclass(frozen=True, slots=True)
class FieldValue:
    field_name: str
    original_value: object
    original_type: str
    normalized_value: object | None
    transformations: tuple[str, ...]
    issues: tuple["ValidationIssue", ...]

Cada linha deve preservar sua origem:

@dataclass(frozen=True, slots=True)
class SourceLocation:
    file_name: str
    sheet_name: str | None
    row_number: int

O registro tratado não deve substituir o registro bruto. Ambos devem permanecer disponíveis até o fim da execução.

8. Identificação da aba e do cabeçalho

O sistema não pode assumir a primeira aba ou a primeira linha.

Cada perfil define:

nomes e aliases de abas;

colunas obrigatórias;

colunas opcionais;

aliases de cabeçalhos;

quantidade máxima de linhas inspecionadas;

pontuação mínima;

diferença mínima entre a primeira e a segunda candidata.

O algoritmo deve:

normalizar temporariamente nomes de abas e cabeçalhos;

procurar possíveis cabeçalhos nas primeiras linhas;

pontuar a presença de colunas obrigatórias e opcionais;

penalizar colunas obrigatórias ausentes e nomes duplicados;

escolher somente quando houver uma candidata inequívoca;

gerar ABA_NAO_ENCONTRADA, ABA_AMBIGUA ou CABECALHO_NAO_ENCONTRADO quando necessário.

O relatório registra a aba original, aba selecionada, linha do cabeçalho, pontuação e colunas mapeadas.

9. Normalização dos cabeçalhos

A normalização usada para comparação pode:

remover espaços externos e duplicados;

remover caracteres invisíveis;

substituir quebras de linha por espaço;

comparar sem acentos;

comparar sem diferença entre maiúsculas e minúsculas;

comparar aliases definidos no perfil.

O título original deve ser preservado. Se duas colunas forem convertidas para o mesmo nome canônico, o sistema gera COLUNA_DUPLICADA e não escolhe silenciosamente.

Exemplo de aliases:

columns:
  cpf:
    required: true
    aliases:
      - CPF
      - C.P.F.
      - cpf participante
      - documento
  email:
    required: false
    aliases:
      - e-mail
      - e mail
      - email participante

10. Tratamento dos dados

Tratamentos automáticos permitidos quando configurados:

remover espaços externos;

reduzir espaços internos repetidos em nomes e descrições;

remover caracteres de controle;

converter quebras indevidas em espaços;

normalizar caixa somente nos campos autorizados;

converter datas por uma lista explícita de formatos;

preservar acentos;

preparar textos para saída sem remover aspas legítimas.

Tratamentos proibidos:

inventar valores ausentes;

substituir silenciosamente conteúdo ambíguo;

completar identificadores com quantidade indefinida de zeros;

remover apóstrofos ou aspas legítimos de nomes;

considerar válido um valor apenas porque ele foi convertido;

alterar o arquivo original.

11. Regra crítica do CPF

CPF é str, nunca int ou float.

A leitura deve preservar zeros à esquerda quando disponíveis.

Para normalização, remover apenas espaços, pontos, hífen e a aspa inicial inserida pelo Excel.

O resultado deve possuir 11 dígitos.

Os dígitos verificadores devem ser validados.

Sequências repetidas devem ser rejeitadas.

Letras ou símbolos inesperados devem gerar erro.

Campo obrigatório vazio deve gerar CPF_VAZIO.

CPF com 10 dígitos pode receber um único zero inicial apenas como tentativa controlada.

A tentativa só é aceita se o CPF com 11 dígitos for matematicamente válido.

A correção aceita deve registrar ZERO_INICIAL_RECOMPOSTO.

Valores menores que 10 dígitos não devem receber preenchimento automático.

Duplicidades devem ser pesquisadas no arquivo, lote e banco, conforme o perfil.

Relatórios e exportações devem formatar CPF como texto.

12. E-mail, nomes, textos e datas

E-mail

remover apenas espaços externos;

comparar duplicidades sem diferenciar caixa;

rejeitar espaços internos, múltiplos @, domínio ausente e pontos consecutivos;

diferenciar sintaxe válida de existência real da caixa postal;

preservar o valor original.

Nomes e textos

aceitar acentos, apóstrofos, hífens e aspas legítimas;

aceitar nomes como Ana D'Ávila e Carla "Cacá" Lima;

rejeitar nomes vazios ou compostos apenas por números ou símbolos;

sinalizar nomes suspeitos para revisão sem inventar correção;

usar parâmetros no banco. Escapar texto apenas quando o formato de saída exigir.

Datas

definir formatos aceitos por perfil;

rejeitar datas impossíveis;

não depender da configuração regional do computador;

armazenar internamente como date ou datetime;

preservar o texto original para auditoria.

13. Perfis de importação

Os perfis devem ser arquivos YAML validados por schema antes do processamento.

Campos mínimos:

profile_id: cargo_update
profile_version: 1
sheet:
  aliases: [Atualização de Cargos, Cargos, Empregados]
  header_scan_limit: 30
  minimum_score: 80
columns: {}
deduplication:
  keys: [cpf, competencia]
database:
  server_env: DB_SERVER
  database: SQLPRODINTRANET
  schema: dbo
  object: tb_contrachequeCargosHistorico
  strategy: upsert

Segredos e senhas não podem aparecer no YAML versionado.

cargo_update

Campos mínimos:

matrícula;

CPF;

nome;

tipo de vínculo;

cargo;

nível;

classe;

situação;

data da alteração;

competência.

O perfil deve diferenciar empregado e estagiário, validar combinações permitidas e impedir atualização por uma chave fraca ou ambígua.

event_attendance

Campos mínimos:

CPF;

nome;

e-mail;

número da inscrição;

ID da pessoa;

ID da inscrição;

evento;

subevento;

presença.

O perfil deve classificar separadamente pessoa não encontrada, divergência cadastral, ausência de inscrição, inscrição em outro evento, ausência de vínculo, ausência de presença e múltiplas inscrições. Os joins não podem multiplicar participantes no relatório final.

14. Banco de dados

O adaptador inicial deve suportar SQL Server.

Regras:

registrar servidor lógico, banco, esquema e objeto;

validar a existência dos objetos necessários antes de processar;

nunca usar SELECT * na aplicação;

usar comandos parametrizados;

usar transações;

processar em lotes configuráveis;

fazer rollback do lote afetado em falha;

manter o relatório mesmo após rollback;

implementar idempotência por hash, perfil e versão do perfil;

registrar quantidade prevista, inserida, atualizada, ignorada e rejeitada;

executar validate e dry-run com credencial sem permissão de escrita sempre que possível;

não esconder regras essenciais exclusivamente em procedures sem documentação e teste de contrato.

A geração de .sql é opcional e serve para revisão. A execução parametrizada é o caminho principal.

15. Relatório de inconsistências

Gerar um único .xlsx por execução.

Aba Resumo

ID da execução;

perfil e versão;

arquivos recebidos, processados e rejeitados;

aba e cabeçalho encontrados;

linhas lidas;

registros válidos;

registros corrigidos automaticamente;

registros em revisão;

registros bloqueados;

total por código de inconsistência;

CPFs com zero recomposto;

duplicidades;

total apto e não apto para importação.

Aba Inconsistencias

ID da execução;

arquivo;

aba;

linha original;

identificador do registro;

campo;

valor original;

valor tratado;

transformações aplicadas;

código;

descrição;

severidade;

ação sugerida;

status;

apto para importar.

Status permitidos:

CORRIGIDO_AUTOMATICAMENTE;

REVISAR;

BLOQUEADO.

Severidades permitidas:

INFO;

ALERTA;

ERRO.

O resumo deve conciliar matematicamente com o detalhe. Nenhum bloqueado pode aparecer no arquivo de importação.

16. Códigos iniciais de inconsistência

ARQUIVO_INVALIDO
FORMATO_NAO_SUPORTADO
ABA_NAO_ENCONTRADA
ABA_AMBIGUA
CABECALHO_NAO_ENCONTRADO
COLUNA_OBRIGATORIA_AUSENTE
COLUNA_DUPLICADA
COLUNA_DESCONHECIDA
CPF_VAZIO
CPF_TAMANHO_INVALIDO
CPF_DIGITO_INVALIDO
CPF_AMBIGUO
CPF_DUPLICADO
ZERO_INICIAL_RECOMPOSTO
EMAIL_INVALIDO
EMAIL_DUPLICADO
NOME_INVALIDO
DATA_INVALIDA
VALOR_INVALIDO
REGISTRO_DUPLICADO
PESSOA_NAO_ENCONTRADA
DIVERGENCIA_CADASTRAL
SEM_INSCRICAO
INSCRICAO_OUTRO_EVENTO
SEM_VINCULO_SUBEVENTO
SEM_PRESENCA
ERRO_BANCO

Novos códigos devem ser adicionados ao enum, documentação e testes. Não usar mensagens livres como identificador técnico.

17. CLI prevista

spreadsheet-importer validate \
  --profile cargo_update \
  --input ./input \
  --output ./output

spreadsheet-importer dry-run \
  --profile cargo_update \
  --input ./input \
  --compare-database

spreadsheet-importer import \
  --profile cargo_update \
  --input ./input \
  --approved-execution-id <uuid>

O comando import não deve aceitar uma execução que possua registros bloqueados ou cujo perfil/arquivo tenha sido alterado depois da aprovação.

18. Configuração e variáveis de ambiente

Usar prefixo SPREADSHEET_IMPORTER_.

SPREADSHEET_IMPORTER_ENVIRONMENT=development
SPREADSHEET_IMPORTER_LOG_LEVEL=INFO
SPREADSHEET_IMPORTER_INPUT_PATH=./input
SPREADSHEET_IMPORTER_OUTPUT_PATH=./output
SPREADSHEET_IMPORTER_CHUNK_SIZE=5000
SPREADSHEET_IMPORTER_DB_SERVER=
SPREADSHEET_IMPORTER_DB_NAME=
SPREADSHEET_IMPORTER_DB_USER=
SPREADSHEET_IMPORTER_DB_PASSWORD=
SPREADSHEET_IMPORTER_DB_DRIVER=ODBC Driver 18 for SQL Server

O repositório deve conter apenas .env.example. O arquivo .env real deve permanecer no .gitignore.

Precedência: argumento da CLI > variável de ambiente > perfil YAML > valor padrão seguro.

19. Padrões de nomenclatura

Python

Elemento

Padrão

Exemplo

Pacotes e módulos

snake_case

spreadsheet_reader.py

Funções e métodos

snake_case

validate_cpf()

Variáveis

snake_case

normalized_cpf

Constantes

UPPER_SNAKE_CASE

DEFAULT_CHUNK_SIZE

Classes

PascalCase

ValidationResult

Exceções

PascalCase com sufixo Error

AmbiguousSheetError

Protocolos

PascalCase por responsabilidade

SpreadsheetReader

Variáveis booleanas

prefixo semântico

is_valid, has_header, can_import

Coleções

nome no plural

input_files, validation_issues

Funções assíncronas

mesmo padrão da ação

load_profile()

Regras adicionais:

usar nomes em inglês no código;

usar português apenas em mensagens destinadas ao usuário e relatórios;

evitar abreviações como val, obj, tmp, proc e dados2;

não usar nomes genéricos como utils.py, helpers.py ou manager.py sem responsabilidade clara;

funções devem representar ações e classes devem representar conceitos;

parâmetros devem explicitar unidade quando necessário, como timeout_seconds;

identificadores como CPF, matrícula e inscrição devem ser str;

não usar prefixos de tipo como str_name ou int_count;

não usar nomes de banco em código de domínio.

Banco de dados

sempre usar o nome qualificado database.schema.object na configuração e documentação;

parâmetros SQL em snake_case;

scripts de migração com sequência e descrição: V001__create_execution_tables.sql;

não criar tabela com prefixo vw_;

views usam vw_, procedures usp_ e tabelas nomes descritivos, quando o padrão institucional permitir;

objetos legados fora do padrão devem ser documentados, não renomeados sem análise de impacto.

Arquivos e saídas

<execution_id>_validation_report.xlsx
<execution_id>_valid_records.csv
<execution_id>_valid_records.json
<execution_id>_manifest.json

20. Versões e dependências

Baseline proposta para a primeira versão:

Componente

Linha adotada

Uso

Python

3.14.x

Runtime principal

pandas

3.0.x

Transformação tabular e lotes

openpyxl

3.1.x

Leitura e relatório .xlsx

xlrd

2.0.x

Leitura exclusiva de .xls

XlsxWriter

3.2.x

Geração do relatório .xlsx

Pydantic

2.13.x

Configurações e contratos

pydantic-settings

mesma linha compatível com Pydantic

Variáveis de ambiente

Typer

0.x estável definido no lock

CLI

SQLAlchemy

2.0.x

Unidade de trabalho e acesso ao banco

pyodbc

versão estável definida no lock

Driver SQL Server

PyYAML

6.x

Perfis YAML

email-validator

2.x

Validação sintática de e-mail

pytest

versão estável definida no lock

Testes

pytest-cov

versão estável definida no lock

Cobertura

Ruff

versão estável definida no lock

Lint e formatação

mypy

versão estável definida no lock

Verificação de tipos

pre-commit

versão estável definida no lock

Controles locais

Regras de versão:

.python-version define a versão exata do Python usada pelo projeto;

pyproject.toml define os intervalos compatíveis;

uv.lock registra todas as versões exatas e hashes;

CI, desenvolvimento e produção usam o mesmo uv.lock;

atualização de dependência ocorre em pull request próprio;

alterações de versão devem executar todos os testes;

versões beta, alpha ou release candidate não entram em produção;

a tabela acima define a linha arquitetural. O lock é a fonte oficial das versões exatas instaladas.

xlrd deve ser usado apenas para o formato histórico .xls. O formato .xlsx deve usar leitor próprio para OOXML.

21. Padrões de código

PEP 8 aplicado pelo Ruff;

type hints em funções públicas e regras de domínio;

limite padrão de 100 caracteres por linha;

docstrings em APIs públicas, decisões não óbvias e regras de negócio;

funções pequenas, com uma responsabilidade principal;

evitar estado global mutável;

preferir composição a herança;

usar pathlib.Path para caminhos;

usar Decimal para valores monetários;

usar date e datetime para datas;

usar timezone explícito nos registros de execução;

capturar exceções apenas quando houver tratamento, contexto ou conversão para erro do domínio;

nunca usar except Exception: pass;

mensagens de log devem ser estruturadas e não concatenadas manualmente;

não incluir CPF, e-mail, senha ou conteúdo completo das linhas nos logs técnicos.

22. Testes e qualidade

Tipos de teste

unitários: normalizadores, validadores, pontuação e políticas;

integração: leitura real dos três formatos e geração do relatório;

contrato: banco, perfis YAML e adaptadores;

regressão: cada problema encontrado em homologação;

desempenho: arquivos grandes e processamento em lotes;

segurança: arquivos inválidos, XML malicioso e fórmulas perigosas.

Casos mínimos:

aba correta fora da primeira posição;

cabeçalho fora da primeira linha;

aba reconhecida por estrutura e aliases;

empate entre abas candidatas;

títulos com acentos, espaços, quebra e caracteres invisíveis;

CPF formatado, numérico, com aspa, sem zero inicial, inválido, vazio e duplicado;

e-mails válidos e inválidos;

nomes com apóstrofos e aspas;

datas inválidas e formatos misturados;

linha vazia no meio do arquivo;

duplicidade no arquivo e no lote;

falha de banco com rollback;

bloqueados ausentes da saída válida;

conciliação entre resumo e detalhes.

Metas iniciais:

100% das regras críticas de CPF testadas;

100% dos códigos de bloqueio com ao menos um teste;

cobertura mínima global de 85%;

nenhum erro de lint, tipos ou teste no branch principal.

Cobertura não substitui qualidade dos cenários.

23. Segurança e privacidade

tratar arquivos recebidos como não confiáveis;

limitar tamanho de arquivo, linhas, colunas e células;

não executar macros;

neutralizar valores iniciados por =, +, - ou @ ao exportar conteúdo não confiável para planilhas, evitando formula injection;

proteger o parser XML contra ataques conhecidos;

armazenar credenciais apenas em variáveis de ambiente ou cofre de segredos;

mascarar dados pessoais em logs;

restringir acesso aos relatórios que contenham CPF e e-mail;

definir prazo de retenção e descarte dos arquivos;

não enviar dados pessoais a serviços externos sem autorização;

registrar quem executou e aprovou uma importação.

24. Logs, auditoria e observabilidade

Cada evento deve conter, quando aplicável:

timestamp;

level;

execution_id;

profile_id;

profile_version;

file_hash;

file_name;

stage;

duration_ms;

contagens;

código técnico do erro.

Logs descrevem o fluxo técnico. O relatório contém os dados necessários para correção negocial. Não duplicar dados pessoais completos nos logs.

25. Controle de versão com Git

Estratégia de branches

main: sempre estável e protegida;

feature/<issue>-<descricao>: nova funcionalidade;

fix/<issue>-<descricao>: correção;

refactor/<issue>-<descricao>: melhoria interna sem mudar comportamento;

docs/<issue>-<descricao>: documentação;

chore/<issue>-<descricao>: manutenção.

Branches devem durar pouco. Não criar branches permanentes por ambiente.

Commits

Usar Conventional Commits:

feat(reader): add xls worksheet detection
fix(cpf): preserve leading zero during normalization
test(report): cover duplicated registration output
docs(readme): document profile versioning
refactor(database): isolate sql server adapter

Cada commit deve:

ter uma alteração lógica principal;

compilar e passar nos testes relacionados;

não conter credenciais, .env, arquivos de produção ou relatórios com dados pessoais;

explicar o motivo quando a alteração não for óbvia.

Pull requests

Toda alteração entra por pull request com:

problema e objetivo;

solução adotada;

impacto e risco;

testes executados;

evidência do relatório quando aplicável;

plano de rollback para mudanças de banco;

atualização de documentação e changelog.

Exigir ao menos uma revisão e pipeline aprovado.

Versionamento da aplicação

Usar Semantic Versioning:

MAJOR: quebra de compatibilidade em CLI, perfil, relatório ou contrato público;

MINOR: nova funcionalidade compatível;

PATCH: correção compatível.

Começar em 0.1.0 durante desenvolvimento. A primeira versão considerada estável será 1.0.0.

Exemplos:

0.1.0: leitura e validações básicas;

0.2.0: perfis iniciais e relatório;

0.3.0: simulação com banco;

0.4.0: importação transacional;

1.0.0: primeira versão homologada.

Usar tags anotadas, como v0.1.0, e manter CHANGELOG.md no padrão Keep a Changelog.

Versionamento dos perfis

O perfil possui versão própria. Mudanças em aliases sem alteração de significado podem incrementar versão menor. Mudança de chave, obrigatoriedade, tipo, destino ou regra de negócio deve criar nova versão do perfil.

Uma execução registra:

versão da aplicação;

versão do perfil;

hash do arquivo de entrada;

hash da configuração;

commit Git, quando disponível.

26. Integração contínua

O pipeline deve executar, nesta ordem:

instalação pelo lock;

validação do pyproject.toml;

Ruff check;

Ruff format check;

mypy;

testes unitários;

testes de integração;

cobertura;

verificação de dependências e segredos;

criação do artefato versionado em tags.

O pipeline não deve acessar banco de produção.

27. Critérios de aceite

O sistema identifica aba e cabeçalho sem posição fixa.

Nenhum CPF perde zero inicial na leitura, relatório ou exportação.

Zero inicial só é recomposto se o CPF resultante for válido.

Aspas e apóstrofos não quebram arquivos nem comandos de banco.

Valor original, tratado e transformações permanecem auditáveis.

Erros remanescentes ficam no relatório e são bloqueados.

O relatório localiza arquivo, aba, linha, campo e ação necessária.

Resumo e detalhes possuem totais conciliados.

validate não altera o banco.

Vários arquivos podem ser processados na mesma execução.

Banco, esquema e objeto ficam explícitos.

Massas .xls e .xlsx estão cobertas por testes automatizados.

Falha de um arquivo não elimina o resultado dos demais.

Uma falha de persistência executa rollback.

Registros bloqueados nunca são importados.

O ambiente é reproduzível a partir de .python-version, pyproject.toml e uv.lock.

28. Definição de pronto

Uma atividade só está pronta quando:

código implementado;

testes adicionados e aprovados;

lint e tipos aprovados;

documentação atualizada;

logs e mensagens revisados;

nenhum dado sensível foi incluído;

critérios de aceite atendidos;

revisão concluída;

changelog atualizado quando necessário;

risco e rollback documentados para mudanças persistentes.

29. Entregáveis

código-fonte Python;

README.md atualizado;

pyproject.toml, .python-version e uv.lock;

perfis cargo_update e event_attendance;

testes e massas de homologação;

relatório de exemplo;

arquivo de válidos de exemplo;

documentação operacional;

ADRs das decisões relevantes;

pipeline de integração contínua;

changelog e tags de versão.

30. Próxima etapa recomendada

Criar somente a Parte 1:

inicializar o repositório;

configurar Python, pyproject.toml e lock;

criar a estrutura de pastas;

configurar Ruff, mypy e pytest;

implementar a CLI com o comando --version;

adicionar o pipeline básico;

registrar a primeira ADR;

publicar a versão 0.1.0-dev.1 apenas para desenvolvimento.

Depois disso, iniciar a leitura dos três formatos usando as massas de teste já preparadas.
