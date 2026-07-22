# ETAPA 2 — AUDITORIA E CORREÇÃO FINAL

> **Status:** APROVADO PARA A PRÓXIMA ETAPA  
> **Data da validação:** 2026-07-21  
> **Workflow DEV:** `ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721` (`NdproODtUwjO9ZZ5`)  
> **Workflow produção:** `ToolsProductsDataTableToRag` (`exIKvB9KjZy5AezC`) — mantido inativo e sem alterações

## Resultado executivo

A configuração foi corrigida no workflow DEV, a ingestão foi executada de forma real, os documentos foram conferidos diretamente no Supabase, o backup foi feito antes da limpeza e os 120 documentos legados foram removidos somente após a autorização explícita registrada na solicitação.

## Correções aplicadas

- O nó `Supabase Vector Store/Hybrid` permanece em modo `insert`, tabela `documents`, locator da tabela válido e credencial `SupaNivanoDonaRosa`.
- O modelo de embeddings é `text-embedding-3-large` com `dimensions: 1536`, compatível com `public.documents.embedding vector(1536)`.
- A idempotência real foi adicionada:
  - `GetExistingVersion` procura o `catalog_hash`;
  - `Idempotency Gate` calcula a decisão;
  - `Idempotency IF` roteia inserção ou salto;
  - `Idempotency Skip` retorna `SKIPPED_ALREADY_EXISTS`.
- O nó de verificação foi configurado com `alwaysOutputData`, e a condição booleana foi corrigida para comparação textual determinística.

## Evidência de ingestão DEV

- Execução n8n **1135**: sucesso.
- Itens ativos lidos da Data Table DEV: **110**.
- Linhas alvo gravadas com `source_version=v_13981aaf`: **110**.
- Metadados presentes: `file_name=product_restaurant_list`, `source_version=v_13981aaf`, `catalog_hash=13981aaf83a38c7f1a810e4242b216bccd426bd003da75dd2e89c4e3b581bac8`, `run_id=run_13981aaf`.

## Backup e limpeza autorizada

Backup completo da tabela antes da exclusão:

- Arquivo: `2-etapa/output/legacy_documents_120_backup.json`
- SHA-256: `f3478a0d968371c3388682d703b2fecb4dd12ed7f2e4bd166aeca76bcfd76103`
- Registros preservados no backup: **120**

Após confirmar a nova versão, foi executada somente esta exclusão restrita:

```sql
DELETE FROM public.documents
WHERE metadata->>'file_name' = 'product_restaurant_list'
  AND metadata->>'source_version' IS NULL;
```

Resultado: **120 linhas excluídas**.

## Estado final confirmado diretamente no Supabase

- Total em `public.documents`: **110**
- Versões presentes: somente `v_13981aaf`
- Hash presente: somente o hash canônico acima
- Embeddings não nulos: **110/110**
- Conteúdo legado (`sabor da terra` / `o site informa`): **0 ocorrências**
- Tipo da coluna: `vector(1536)`
- RPC `hybrid_search`: existente e executável (probe válido retornou 5 linhas)
- RPC `match_documents`: existente e executável (probe válido retornou 5 linhas)

## Prova de idempotência

- Execução n8n **1136**: sucesso.
- O gate encontrou **110** documentos da mesma versão/hash.
- Rota executada: `Idempotency Skip`.
- Status retornado: `SKIPPED_ALREADY_EXISTS`.
- Nova ingestão nessa segunda execução: **0**.

A evidência está em `2-etapa/output/idempotency_proof.json`.

## Observação sobre a matriz semântica

Não foi fabricada uma matriz semântica de 10 consultas. O arquivo `hybrid_search_matrix_results.json` registra apenas os probes estruturais realmente executados; a validação de relevância por consultas de negócio deve ser feita na próxima etapa, através do endpoint/Edge Function que gera o embedding da consulta.

## Artefatos principais

- `2-etapa/output/reconfigured_workflow_dev.json`
- `2-etapa/output/idempotency_proof.json`
- `2-etapa/output/legacy_documents_120_backup.json`
- `2-etapa/output/legacy_documents_120_backup.sha256`
- `2-etapa/output/hybrid_search_matrix_results.json`

