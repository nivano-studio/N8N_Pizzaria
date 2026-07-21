-- Live reconciled RAG schema archive.
-- Supabase project: qucikffpvnvzaxfyugwi
-- Collected/reconciled: 2026-07-21T20:11:09Z
--
-- This is an archive of the live catalog and the two current RPC definitions.
-- It is intentionally not a bootstrap migration: applying CREATE TABLE or CREATE
-- INDEX statements to an existing project without IF NOT EXISTS would fail.

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

CREATE OR REPLACE FUNCTION public.hybrid_search(
  query_text text,
  query_embedding extensions.vector,
  match_count integer,
  full_text_weight double precision DEFAULT 1,
  semantic_weight double precision DEFAULT 1,
  rrf_k integer DEFAULT 50
)
RETURNS SETOF public.documents
LANGUAGE sql
SECURITY INVOKER
SET search_path = public, extensions
AS $function$
WITH full_text AS (
  SELECT
    d.id,
    row_number() OVER (
      ORDER BY ts_rank_cd(d.fts, websearch_to_tsquery(query_text)) DESC
    ) AS rank_ix
  FROM public.documents AS d
  WHERE d.fts @@ websearch_to_tsquery(query_text)
  ORDER BY rank_ix
  LIMIT LEAST(match_count, 30) * 2
),
semantic AS (
  SELECT
    d.id,
    row_number() OVER (ORDER BY d.embedding <#> query_embedding) AS rank_ix
  FROM public.documents AS d
  ORDER BY rank_ix
  LIMIT LEAST(match_count, 30) * 2
)
SELECT d.*
FROM full_text
FULL OUTER JOIN semantic ON full_text.id = semantic.id
JOIN public.documents AS d
  ON COALESCE(full_text.id, semantic.id) = d.id
ORDER BY
  COALESCE(1.0 / (rrf_k + full_text.rank_ix), 0.0) * full_text_weight +
  COALESCE(1.0 / (rrf_k + semantic.rank_ix), 0.0) * semantic_weight DESC
LIMIT LEAST(match_count, 30)
$function$;

CREATE OR REPLACE FUNCTION public.match_documents(
  query_embedding extensions.vector(1536),
  match_threshold double precision DEFAULT 0,
  match_count integer DEFAULT 10
)
RETURNS TABLE (
  id bigint,
  content text,
  metadata jsonb,
  similarity double precision
)
LANGUAGE sql
SECURITY INVOKER
SET search_path = public, extensions
AS $function$
  SELECT
    d.id,
    d.content,
    d.metadata,
    (1 - (d.embedding <=> query_embedding))::double precision AS similarity
  FROM public.documents AS d
  WHERE d.embedding IS NOT NULL
    AND (1 - (d.embedding <=> query_embedding)) > match_threshold
  ORDER BY d.embedding <=> query_embedding
  LIMIT LEAST(match_count, 30)
$function$;

REVOKE ALL ON FUNCTION public.match_documents(extensions.vector, double precision, integer) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.match_documents(extensions.vector, double precision, integer) FROM anon, authenticated;
GRANT EXECUTE ON FUNCTION public.match_documents(extensions.vector, double precision, integer) TO service_role;
