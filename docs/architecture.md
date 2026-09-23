# Arquitetura

## Fluxo

```text
Arquivo -> leitor -> identificação da aba/cabeçalho -> normalização
       -> validação -> deduplicação -> regras do perfil -> relatório
       -> simulação/importação
```

## Limites de responsabilidade

- O domínio não conhece Excel, CSV, banco de dados ou CLI.
- Leitores retornam valores brutos e sua origem.
- Normalizadores aplicam transformações explícitas.
- Validadores retornam inconsistências; não gravam dados.
- Casos de uso orquestram o fluxo.
- Adaptadores implementam leitura, banco e relatórios.
- Perfis descrevem layouts e regras variáveis.

## Estados do registro

- `APPROVED`: apto para a próxima etapa.
- `CORRECTED`: corrigido por regra segura e auditável.
- `REVIEW`: precisa de análise humana.
- `BLOCKED`: não pode ser importado.

