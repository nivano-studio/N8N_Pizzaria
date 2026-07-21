# ETAPA 1 — REVISÃO DE AUDITORIA

> **Revisão:** `2026-07-21T21:35:36Z`  
> **Data Table alvo:** `products__DEV_DONA_ROSA_20260721` (`yEPAXmN9AQQMn8IU`)

## Decisão

```text
PENDENTE — correções e confirmação necessárias antes de avançar para o RAG
```

## Resultados confirmados

- `products.corrected.csv` e `canonical_catalog.json` têm 242 registros.
- A distribuição é 112 pizzas tradicionais, 56 especiais, 32 doces, 10 pastéis, 10 porções/aperitivos e 22 bebidas.
- `name` é único; preços são parseáveis; `image_url` e `active` estão preenchidos; não há `o site informa`, `Sabor da Terra` ou segredo em texto claro.
- O catálogo é semanticamente baseado no cardápio oficial e os workflows de produção permanecem topologicamente iguais aos backups.
- O workflow DEV continua inativo, isolado e sem nós externos classificados habilitados.

## Correções aplicadas no pacote

- As 25 descrições de pizzas Extra foram corrigidas para manter `Extra (70x70cm)`.
- `catalog_diff_report.json` e `.md` foram recalculados com correspondência explícita dos 14 nomes antigos de bebidas; o relatório anterior classificava 25 itens existentes como `NEW_UNMATCHED`.
- Os relatórios anteriores foram preservados como `ETAPA1_STATUS_PRIOR.md`.

## Pendências que impedem aprovação

1. Os artefatos de execução não são internamente consistentes: o log de desativação registra 13 extras inativos e 243 ativos, enquanto o relatório declara 14 inativos e 242 ativos. A prova de idempotência verifica apenas total 256 e diff zero.
2. O log declara `deactivated_requested_by_user=true`, mas não contém a confirmação explícita exigida antes de desativar/excluir registros extras.
3. O conector n8n disponível nesta sessão permite confirmar existência/schema da Data Table, mas não expõe leitura de linhas. Portanto não consigo certificar ao vivo a contagem final por `active` sem uma exportação/leitura adicional.
4. O checksum original cobria somente `0-etapa`; a Etapa 1 não possuía manifesto próprio.
5. A Etapa 0 foi aprovada anteriormente apesar de ter aplicado uma migração estrutural no Supabase, algo proibido pelo Prompt 0. Essa decisão precisa ser reavaliada antes de considerar a cadeia completa conforme.

## Ação necessária do usuário

Confirme se a desativação dos registros extras foi autorizada e forneça uma exportação da Data Table DEV (ou habilite uma operação de leitura) para eu verificar 242 ativos canônicos e 14 inativos. Também confirme se a migração RAG do Supabase deve permanecer; não a reverti automaticamente porque isso pode quebrar a consulta do workflow RAG.
