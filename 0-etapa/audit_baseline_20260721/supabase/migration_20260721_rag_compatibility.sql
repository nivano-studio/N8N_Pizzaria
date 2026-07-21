-- Applied to Supabase project qucikffpvnvzaxfyugwi on 2026-07-21.
-- Purpose: restore the RPC required by n8n's Supabase Vector Store and
-- fix the mutable search_path warning on the existing hybrid_search RPC.
-- No table, vector, policy, or data mutation was performed.

CREATE OR REPLACE FUNCTION public.match_documents(
  query_embedding extensions.vector(1536),
  match_threshold double precision DEFAULT 0,
  match_count integer DEFAULT 10
)
RETURNS TABLE (id bigint, content text, metadata jsonb, similarity double precision)
LANGUAGE sql
SECURITY INVOKER
SET search_path = public, extensions
AS $function$
  SELECT d.id, d.content, d.metadata,
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
  SELECT d.id,
         row_number() OVER (ORDER BY ts_rank_cd(d.fts, websearch_to_tsquery(query_text)) DESC) AS rank_ix
  FROM public.documents AS d
  WHERE d.fts @@ websearch_to_tsquery(query_text)
  ORDER BY rank_ix
  LIMIT LEAST(match_count, 30) * 2
),
semantic AS (
  SELECT d.id,
         row_number() OVER (ORDER BY d.embedding <#> query_embedding) AS rank_ix
  FROM public.documents AS d
  ORDER BY rank_ix
  LIMIT LEAST(match_count, 30) * 2
)
SELECT d.*
FROM full_text
FULL OUTER JOIN semantic ON full_text.id = semantic.id
JOIN public.documents AS d ON COALESCE(full_text.id, semantic.id) = d.id
ORDER BY COALESCE(1.0 / (rrf_k + full_text.rank_ix), 0.0) * full_text_weight +
         COALESCE(1.0 / (rrf_k + semantic.rank_ix), 0.0) * semantic_weight DESC
LIMIT LEAST(match_count, 30)
$function$;
