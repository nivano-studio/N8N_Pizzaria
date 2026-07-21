# ETAPA 0 — RELATÓRIO FINAL

> **Validação concluída:** `2026-07-21T20:57:45Z`  
> **Ambientes verificados:** n8n live e Supabase `qucikffpvnvzaxfyugwi`

## Resultado

```text
APROVADA — Etapa 1 autorizada
```

## Evidências verificadas

| Item | Resultado |
| --- | --- |
| Workflows DEV | Os três workflows DEV existem, estão inativos, sem triggers e com `availableInMCP=true`. |
| Isolamento | Exports DEV não contêm IDs legados de produção/Data Tables. |
| Nós externos | Todos os nós externos classificados nos DEV estão desabilitados. |
| Segredos | A chave publicável residual de um nó HTTP DEV desabilitado foi removida/redigida live; a nova varredura encontrou zero padrões de chave/JWT. |
| Data Tables DEV | As três tabelas DEV do projeto `mNx2JLqnsOgn6t6X` existem com os schemas arquivados; contagens evidenciadas: products 242, customers 1, invoices 2. |
| Rollback | Evidência arquivada de restauração descartável: 85 nós, 69 conexões e exclusão confirmada. |
| Supabase/RAG | `match_documents` foi criada e testada; `hybrid_search` foi endurecida com `SECURITY INVOKER` e `search_path` fixo. Ambos os probes retornaram um resultado. |
| Integridade do pacote | `checksums.sha256` é regenerado e validado pelo finalizador local após a emissão deste relatório. |

## Alterações realizadas nesta finalização

- O artefato de DDL/RPC foi reconciliado com o catálogo vivo: `extensions.vector(1536)`, índice HNSW `vector_ip_ops`, RLS habilitado sem policies e definições reais das RPCs.
- Foi aplicada, sob autorização, uma migração controlada no Supabase para criar `public.match_documents` e fixar o `search_path` de `public.hybrid_search`.
- Foi removida/redigida a chave publicável armazenada em um nó HTTP desabilitado do workflow DEV `x7L6Z0klfhvqWx1R`.

Não houve alteração em workflow n8n de produção, Data Table de produção ou linha de `public.documents`.

## Avisos registrados, sem bloqueio da Etapa 0

- `public.documents` permanece com RLS habilitado e nenhuma policy, conforme o desenho existente de acesso por `service_role`.
- O advisor do Supabase ainda aponta `public.rls_auto_enable()` como `SECURITY DEFINER` executável por `anon` e `authenticated`. É um objeto preexistente e fora do escopo da correção RAG; requer decisão funcional antes de ser alterado.
- O conector n8n reporta compatibilidade de schema em um nó `OpenAI1` legado com recurso `audio`; esse nó já está desabilitado no DEV. Ele foi preservado para manter a topologia do backup e não é executável enquanto a Etapa 0 estiver isolada.

As evidências técnicas estão em `audit_baseline_20260721/`, incluindo migração, metadados, probes, rollback e manifest SHA-256.
