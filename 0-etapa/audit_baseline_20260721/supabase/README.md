# Evidência Supabase/RAG — Etapa 0

- Projeto: `qucikffpvnvzaxfyugwi`
- Tabela RAG: `public.documents` (120 linhas)
- Embedding: `extensions.vector(1536)`
- Índice vetorial: HNSW com `extensions.vector_ip_ops`
- RLS: habilitado; nenhuma policy existe atualmente. O acesso do n8n é restrito ao `service_role`.

## Arquivos

- `documents_schema.sql`: DDL reconstruído do catálogo PostgreSQL ao vivo.
- `rpc_definitions.sql`: definições completas e atuais de `hybrid_search` e `match_documents`.
- `migration_20260721_rag_compatibility.sql`: migração aplicada sob autorização para criar `match_documents` e fixar o `search_path` de `hybrid_search`.
- `documents_metadata.json` e `catalog_evidence.json`: metadados e resultados de verificação.

## Resultado

O n8n referencia `match_documents` no nó `Supabase Vector Store/Hybrid`. Essa RPC foi criada, testada com uma consulta vetorial controlada e restringida ao papel `service_role`. As funções usam `SECURITY INVOKER` e `search_path` fixo (`public, extensions`).

Nenhum workflow n8n de produção, Data Table de produção ou linha da tabela `documents` foi alterado.
