-- Supabase project: qucikffpvnvzaxfyugwi
-- Source: live PostgreSQL catalog queried read-only via Supabase MCP
-- Collected: 2026-07-21T20:11:09Z
-- This schema is reconstructed from live catalog metadata.

CREATE TABLE public.documents (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  content text NOT NULL DEFAULT ''::text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  fts tsvector GENERATED ALWAYS AS (
    to_tsvector('english'::regconfig, COALESCE(content, ''::text))
  ) STORED,
  embedding vector(1536),
  CONSTRAINT documents_pkey PRIMARY KEY (id)
);

CREATE INDEX documents_embedding_idx
  ON public.documents USING hnsw (embedding vector_ip_ops);

CREATE INDEX documents_fts_idx
  ON public.documents USING gin (fts);

-- Live catalog result: no RLS policies were returned for public.documents.
