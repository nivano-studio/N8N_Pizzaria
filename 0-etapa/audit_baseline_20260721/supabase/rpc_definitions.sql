-- Supabase project: qucikffpvnvzaxfyugwi
-- Source: pg_get_functiondef(...) queried read-only via Supabase MCP
-- Collected: 2026-07-21T20:11:09Z

CREATE OR REPLACE FUNCTION public.hybrid_search(query_text text, query_embedding vector, match_count integer, full_text_weight double precision DEFAULT 1, semantic_weight double precision DEFAULT 1, rrf_k integer DEFAULT 50)
 RETURNS SETOF documents
 LANGUAGE sql
AS $function$
with full_text as (
 select
 id,
 -- Note: ts_rank_cd is not indexable but will only rank matches of the where clause
 -- which shouldn't be too big
 row_number() over(order by ts_rank_cd(fts, websearch_to_tsquery(query_text)) desc) as rank_ix
 from
 documents
 where
 fts @@ websearch_to_tsquery(query_text)
 order by rank_ix
 limit least(match_count, 30) * 2
),
semantic as (
 select
 id,
 row_number() over (order by embedding <#> query_embedding) as rank_ix
 from
 documents
 order by rank_ix
 limit least(match_count, 30) * 2
)
select
 documents.*
from
 full_text
 full outer join semantic
 on full_text.id = semantic.id
 join documents
 on coalesce(full_text.id, semantic.id) = documents.id
order by
 coalesce(1.0 / (rrf_k + full_text.rank_ix), 0.0) * full_text_weight +
 coalesce(1.0 / (rrf_k + semantic.rank_ix), 0.0) * semantic_weight
 desc
limit
 least(match_count, 30)
$function$;

-- Live catalog result: public.match_documents was not found in the queried project.
