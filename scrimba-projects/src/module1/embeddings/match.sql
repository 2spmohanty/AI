
create or replace function match_documents (
  query_embedding extensions.vector(1536),
  match_threshold float,
  match_count int
)
returns setof documents
language sql
as $$
  select *
  from documents
  where documents.embedding <=> query_embedding < 1 - match_threshold
  order by documents.embedding <=> query_embedding asc
  limit least(match_count, 200);
$$;


create or replace function match_documents (
  query_embedding extensions.vector(1536),
  match_threshold float, -- Now behaves like a standard percentage (e.g., 0.70)
  match_count int
)
returns setof documents
language sql
as $$
  select *
  from documents
  -- Fixed: Changed (1 - distance) to represent standard similarity
  where (1 - (documents.embedding <=> query_embedding)) > match_threshold
  order by documents.embedding <=> query_embedding asc
  limit least(match_count, 200);
$$;
