# Prompt — correção dos bloqueios restantes da Etapa 0

Trabalhe diretamente na pasta `0-etapa` do projeto Antigravity. Não use ZIP como requisito e não inicie a Etapa 1.

O novo pacote já confirma estes pontos: workflows DEV inativos, `availableInMCP=true`, Data Tables DEV no projeto correto, zero IDs de produção/antigos nos DEV, zero nós externos habilitados e rollback descartável removido. Não refaça alterações de produção.

Corrija apenas os bloqueios restantes abaixo.

## 1. Sanitização completa de segredos

Faça uma varredura recursiva em todos os arquivos dentro de `0-etapa`, incluindo backups, exports DEV, scripts, relatórios e manifests.

Detecte e substitua, sem mostrar os valores:

- chaves `sb_...` e `sb_publishable_...`;
- valores `Bearer ...`;
- chaves `sk-...`, JWTs e tokens ElevenLabs/Supabase/OpenAI;
- qualquer valor estático em headers, query parameters, URLs ou parâmetros de nós.

O pacote anterior ainda continha um valor `sb_...` no backup e no export DEV. Substitua-o por `[REDACTED_SECRET]` ou por referência segura a credencial n8n.

Atualize o validador para procurar pelo menos estas expressões:

```regex
sb_[A-Za-z0-9_-]{20,}
Bearer\s+[A-Za-z0-9._-]{20,}
sk-[A-Za-z0-9]{20,}
eyJ[A-Za-z0-9_-]{20,}
```

Ignore apenas os próprios padrões regex escritos nos scripts; nunca ignore valores encontrados em JSON, Markdown, export, backup ou log. O resultado final deve ser zero segredo em texto claro.

## 2. Obter manualmente o schema real do Supabase/RAG

Não invente DDL com base em um resumo. Use o projeto Supabase que alimenta o nó de busca vetorial/híbrida do workflow de produção.

### Opção A — SQL Editor do Supabase

Abra o projeto no Dashboard do Supabase, entre em **SQL Editor**, crie uma consulta somente leitura e execute separadamente os comandos abaixo. Não execute `CREATE`, `ALTER`, `DROP`, `INSERT`, `UPDATE` ou `DELETE`.

#### Colunas e tipos reais da tabela `documents`

```sql
SELECT
  n.nspname AS schema_name,
  c.relname AS table_name,
  a.attnum AS ordinal_position,
  a.attname AS column_name,
  format_type(a.atttypid, a.atttypmod) AS data_type,
  NOT a.attnotnull AS is_nullable,
  pg_get_expr(d.adbin, d.adrelid) AS default_expression,
  col_description(a.attrelid, a.attnum) AS column_comment
FROM pg_attribute a
JOIN pg_class c ON c.oid = a.attrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
WHERE n.nspname = 'public'
  AND c.relname = 'documents'
  AND a.attnum > 0
  AND NOT a.attisdropped
ORDER BY a.attnum;
```

#### Índices reais

```sql
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'documents'
ORDER BY indexname;
```

#### Constraints e políticas RLS

```sql
SELECT
  conname,
  contype,
  pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'public.documents'::regclass
ORDER BY conname;

SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename = 'documents'
ORDER BY policyname;
```

#### Corpo completo das RPCs

```sql
SELECT
  n.nspname AS schema_name,
  p.oid AS function_oid,
  p.proname AS function_name,
  pg_get_function_identity_arguments(p.oid) AS identity_arguments,
  pg_get_function_result(p.oid) AS return_type,
  pg_get_functiondef(p.oid) AS complete_function_definition
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'public'
  AND p.proname IN ('hybrid_search', 'match_documents')
ORDER BY p.proname, p.oid;
```

Copie os resultados completos para arquivos dentro de:

`0-etapa/audit_baseline_20260721/supabase/`

Use, no mínimo:

- `documents_metadata.json` — resultado das consultas de colunas, índices, constraints e RLS;
- `rpc_definitions.sql` — corpo completo retornado por `pg_get_functiondef`;
- `README.md` — projeto consultado, data/hora, origem e instruções de rollback.

### Opção B — dump somente de schema

Se houver acesso seguro à conexão PostgreSQL do projeto, gere um dump somente de schema com `pg_dump`. Nunca coloque a senha em arquivos, prompts, commits ou relatórios.

```bash
pg_dump "$DATABASE_URL" \
  --schema-only \
  --no-owner \
  --no-privileges \
  > 0-etapa/audit_baseline_20260721/supabase/supabase_schema_full.sql
```

O arquivo precisa conter o `CREATE TABLE public.documents`, índices, constraints e o corpo `CREATE FUNCTION`/`CREATE OR REPLACE FUNCTION` das RPCs. Um JSON que apenas lista nomes, parâmetros ou tipos não é DDL suficiente.

Se não houver acesso ao Dashboard nem à conexão PostgreSQL, não fabrique evidência: marque o critério como `PENDENTE`.

## 3. Corrigir o validador Supabase

O validador não pode considerar o critério aprovado apenas porque `documents_schema_and_rpc.json` existe. Ele deve exigir:

- pelo menos um arquivo SQL real com DDL da tabela;
- `CREATE FUNCTION` ou `CREATE OR REPLACE FUNCTION` para `hybrid_search` e/ou `match_documents`;
- colunas, índices, constraints e políticas documentados;
- arquivo de origem e data/hora da coleta.

Se faltar qualquer um desses itens, o status deve ser `FAIL`.

## 4. Regenerar checksums na ordem correta

Depois de concluir todas as edições, execute nesta ordem:

1. sanitização de segredos;
2. inclusão dos arquivos SQL/JSON do Supabase;
3. execução dos validadores;
4. gravação final de `validation_results.json`;
5. geração de `audit_baseline_20260721/checksums.sha256` usando somente arquivos existentes dentro de `0-etapa`;
6. verificação do manifest;
7. geração/atualização de `ETAPA0_STATUS_FINAL.md` antes do checksum final, ou inclua o relatório final no manifest e gere novamente;
8. verificação final do manifest.

Depois da última geração do checksum, não altere mais nenhum arquivo incluído no manifest. O resultado obrigatório é zero ausências e zero divergências. O pacote anterior tinha divergência em `validation_results.json`; isso precisa desaparecer.

## 5. Relatório final

Atualize `0-etapa/ETAPA0_STATUS_FINAL.md` e `audit_baseline_20260721/validation_results.json` com os resultados reais. Não copie `PASS` de relatórios anteriores.

Só use:

```text
APROVADA — Etapa 1 autorizada
```

se:

- nenhum segredo claro existir;
- o checksum estiver 100% válido;
- o DDL real e os corpos das RPCs estiverem arquivados;
- os validadores detectarem esses itens corretamente;
- workflows DEV e Data Tables continuarem isolados e inativos.

Caso contrário, use:

```text
PENDENTE — Etapa 1 NÃO autorizada
```

Não altere produção, não publique workflows, não execute rede/IA/WhatsApp e não faça mudanças estruturais no Supabase.
