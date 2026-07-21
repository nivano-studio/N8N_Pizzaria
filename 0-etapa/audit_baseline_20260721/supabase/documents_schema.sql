-- Live catalog evidence, reconstructed from PostgreSQL metadata.
-- Supabase project: qucikffpvnvzaxfyugwi
-- Collected and reconciled: 2026-07-21T20:11:09Z

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

CREATE TABLE public.documents (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  content text NOT NULL DEFAULT ''::text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  fts tsvector GENERATED ALWAYS AS (
    to_tsvector('english'::regconfig, COALESCE(content, ''::text))
  ) STORED,
  embedding extensions.vector(1536),
  CONSTRAINT documents_pkey PRIMARY KEY (id)
);

CREATE INDEX documents_embedding_idx
  ON public.documents USING hnsw (embedding extensions.vector_ip_ops);

CREATE INDEX documents_fts_idx
  ON public.documents USING gin (fts);

ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- The live catalog has no RLS policies on public.documents.
