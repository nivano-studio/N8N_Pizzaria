# Supabase/RAG evidence

- Project ID: `qucikffpvnvzaxfyugwi`
- Collection mode: read-only Supabase MCP
- Collection date: `2026-07-21T20:11:09Z`
- Table: `public.documents`
- Rows observed: `120`
- Embedding type: `vector(1536)`
- Embedding index: HNSW using `vector_ip_ops`
- Full-text index: GIN on `fts`
- RPC definition: `rpc_definitions.sql`
- Reconstructed catalog schema: `documents_schema.sql`
- Raw catalog evidence: `catalog_evidence.json`

Important: `hybrid_search` exists with six arguments (three required and three defaults). `match_documents` was not found in the live `public` schema and must not be claimed as present without separate evidence.

No DDL, RPC, policy, or data changes were executed during collection.
