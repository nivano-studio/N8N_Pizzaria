# Prompt definitivo — finalização e aprovação da Etapa 0

Você é o agente responsável por concluir a Etapa 0 do projeto n8n da Pizzaria Dona Rosa.

## Escopo e localização

Trabalhe diretamente na pasta local `0-etapa` do projeto Antigravity. O material não está em um arquivo ZIP. Não crie um novo ZIP como condição de conclusão.

Use o n8n MCP e as skills n8n disponíveis para consultar e validar a instância ao vivo. Use os arquivos de entrada já presentes no workspace, incluindo snapshots, exports, `hybrid-search` e documentos da Pizzaria Dona Rosa.

Não inicie a Etapa 1. Não altere regras de negócio, prompts funcionais, preços, taxas, endereços, catálogo ou comportamento de produção.

## Regra de segurança absoluta

Antes de qualquer alteração, registre um baseline imutável dos workflows e Data Tables de produção. Nenhuma operação desta etapa pode editar, publicar, executar, apagar ou reconfigurar produção.

Workflows de produção esperados:

- `ImportPdfToTable` — `vpPp34JIYrReJxM5`
- `ToolsProductsDataTableToRag` — `exIKvB9KjZy5AezC`
- `EvolutionDeliveyRagHibridoDataTables-export` — `XCZsECfv1SNrLN80`

Se algum ID não corresponder ao nome consultado ao vivo, pare e registre o bloqueio. Não adivinhe IDs.

## Objetivo obrigatório

Só declare a Etapa 0 como APROVADA quando todos os critérios abaixo tiverem evidência verificável. Se um único critério falhar, o resultado final deve ser `PENDENTE — Etapa 1 NÃO autorizada`.

## 1. Confirmar a instância ao vivo

1. Verifique a saúde da instância n8n, a versão e o projeto correto.
2. Registre URL, versão, projeto e data/hora em `0-etapa/ETAPA0_STATUS_FINAL.md`.
3. Consulte ao vivo, por nome e por ID, os três workflows DEV.
4. Garanta que os três workflows DEV tenham IDs próprios, nomes com o sufixo `__DEV_DONA_ROSA_20260721` e `active=false`.
5. Habilite o acesso MCP dos três workflows DEV (`availableInMCP=true`) sem publicá-los e sem ativá-los. Depois confirme essa propriedade ao vivo.

Workflows DEV esperados, sujeitos à confirmação ao vivo:

- `ImportPdfToTable__DEV_DONA_ROSA_20260721` — `fq4UCwZ6KOOXm0NY`
- `ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721` — `NdproODtUwjO9ZZ5`
- `EvolutionDeliveyRagHibridoDataTables-export__DEV_DONA_ROSA_20260721` — `x7L6Z0klfhvqWx1R`

## 2. Criar e confirmar Data Tables DEV isoladas

Confirme ao vivo, no mesmo projeto, estas três Data Tables:

- `products__DEV_DONA_ROSA_20260721` — `yEPAXmN9AQQMn8IU`
- `customers__DEV_DONA_ROSA_20260721` — `DacGOSDHaMAFF3Zq`
- `invoices__DEV_DONA_ROSA_20260721` — `0iESK6xkLcCfCNUu`

Se alguma não existir, crie-a com o schema do snapshot correspondente. Popule as cópias a partir dos snapshots locais, sem alterar as Data Tables de produção. Confirme schema, projeto, quantidade de linhas e IDs ao vivo.

Salve em `0-etapa/audit_baseline_20260721/dev_datatables_meta.json` um mapa JSON real com nome, ID, projeto, schema e quantidade de linhas. O arquivo não pode ficar vazio nem conter placeholders.

## 3. Corrigir integralmente os exports DEV

Regenere os exports DEV a partir dos backups de produção, mas atribua a cada cópia um ID DEV próprio e `active=false`.

Em todos os nós DEV que usam Data Tables n8n:

1. Substitua referências aos IDs de produção:
   - `hICNaSYRSMkjHiTT` → `yEPAXmN9AQQMn8IU`
   - `eXHmu98SYFK7A6zN` → `DacGOSDHaMAFF3Zq`
   - `BaMD12kIM3Y5iQDv` → `0iESK6xkLcCfCNUu`
2. Remova também referências antigas de outros projetos, incluindo `XbYdEIzrF5Ltlrll` e `AIwE75J1sVmYQjdk`.
3. Verifique cada nó de leitura, inserção, atualização e exclusão individualmente.
4. Não altere referências Supabase legítimas à tabela `documents` ou à RPC/vector search durante esta substituição; diferencie Data Table n8n de tabela Supabase.
5. Faça uma busca recursiva nos JSON DEV por todos os IDs acima e por referências de produção. O resultado obrigatório é zero referência de produção/IDs antigos.
6. Confirme que os nós DEV apontam exclusivamente para as três Data Tables DEV autorizadas.

## 4. Neutralizar todos os efeitos externos no DEV

Nas cópias DEV, desabilite (`disabled=true`) todos os triggers e todos os nós que possam acessar rede, serviços externos, credenciais ou alterar sistemas externos, incluindo:

- Webhook, chat trigger, form trigger, schedule trigger e manual trigger;
- HTTP Request e HTTP Request Tool;
- Evolution API, WhatsApp, ElevenLabs e Redis;
- Supabase, Supabase Vector Store e chamadas de Edge Function/RPC externas;
- OpenAI, OpenAI Chat Model, OpenAI Embeddings e qualquer nó LangChain que use credencial externa;
- nós de envio, exclusão, escrita ou atualização fora das Data Tables DEV autorizadas.

Isto inclui explicitamente o nó `OpenAI Chat Model1`, que não pode permanecer habilitado.

Para nós HTTP que permaneçam no JSON por necessidade de topologia, substitua URLs por `http://127.0.0.1:9999/disabled_dev_stub`, mantenha-os desabilitados e documente isso. Nenhum workflow DEV pode ser executado para testar rede, IA, WhatsApp, Supabase, Redis ou produção.

Faça auditoria por tipo de nó e por estado `disabled`. O único acesso persistente permitido no DEV é leitura/escrita nas Data Tables DEV autorizadas, e nenhum trigger pode iniciar execução automaticamente.

## 5. Remover segredos dos arquivos

Faça uma varredura recursiva em todos os JSON, scripts, relatórios e manifests dentro de `0-etapa`.

- Não deixe tokens, chaves, JWTs, valores `Bearer`, `sb_...`, `sk-...`, chaves ElevenLabs, Supabase ou OpenAI em texto claro.
- Substitua valores estáticos por `[REDACTED_SECRET]` ou por referência segura a credencial n8n sem expor o valor.
- Não mostre nenhum segredo no relatório, terminal ou resposta final.
- Não rotacione credenciais de produção automaticamente. Apenas registre que a rotação deve ser feita separadamente, caso necessário.

Depois da sanitização, repita a busca e informe apenas contagens e nomes de arquivos afetados, nunca os valores.

## 6. Evidência real de rollback

Execute um teste de rollback em workflow descartável:

1. Crie um workflow temporário a partir de um backup.
2. Confirme ao vivo que ele está inativo e que a contagem de nós e conexões coincide com o backup.
3. Registre data/hora, ID temporário, contagens e resultado.
4. Apague o workflow temporário.
5. Confirme ao vivo que ele não existe mais.

Salve o log sanitizado em `0-etapa/audit_baseline_20260721/rollback_test_evidence.json`. Um script sem log de execução não é evidência suficiente.

## 7. DDL, schema e RPC do Supabase

Arquive dentro de `0-etapa/audit_baseline_20260721/supabase/`:

- DDL/schema da tabela `documents`;
- definição completa da RPC `hybrid_search` ou `match_documents` usada pelo workflow;
- tipo, dimensão e métrica do embedding;
- índices, constraints e permissões relevantes;
- origem/data da evidência e instruções de rollback.

Use somente leitura/introspecção. Não faça alterações estruturais no Supabase. Se não for possível obter qualquer item, não marque o critério como concluído e declare o bloqueio.

## 8. Checksums reproduzíveis

Gere `0-etapa/audit_baseline_20260721/checksums.sha256` usando apenas arquivos que realmente existam dentro de `0-etapa`. Use caminhos relativos POSIX (`/`), ordenados, e exclua o próprio manifest durante o cálculo.

Inclua todos os backups, snapshots, exports DEV, scripts, relatórios, DDL/RPC e demais evidências. Depois execute a verificação do manifest. O resultado obrigatório é:

- zero arquivo ausente;
- zero hash divergente;
- zero referência a arquivos externos ao diretório `0-etapa`.

## 9. Validadores obrigatórios antes da decisão

Execute e preserve os resultados de validadores que comprovem:

- JSON válido de todos os backups e exports DEV;
- IDs DEV próprios e `active=false`;
- `availableInMCP=true` nos três DEV;
- zero IDs de produção ou IDs antigos nos DEV;
- zero nó externo habilitado nos DEV;
- zero segredo em texto claro;
- Data Tables DEV existentes, no projeto correto, com schema e linhas esperados;
- rollback criado, comparado e removido;
- checksums 100% válidos;
- DDL/RPC arquivados.

Salve os resultados em `0-etapa/audit_baseline_20260721/validation_results.json`.

## 10. Relatório final obrigatório

Crie ou substitua `0-etapa/ETAPA0_STATUS_FINAL.md` com:

1. data/hora e instância verificadas;
2. tabela de workflows de produção e DEV com IDs, `active`, `availableInMCP`, nós e conexões;
3. tabela de Data Tables DEV com IDs, projeto, schema e linhas;
4. lista de arquivos de backup/evidência;
5. resultado de cada validador;
6. resultado do rollback;
7. resultado dos checksums;
8. localização do DDL/RPC;
9. bloqueios, se houver;
10. decisão final inequívoca.

Use exatamente uma destas decisões:

- `APROVADA — Etapa 1 autorizada`
- `PENDENTE — Etapa 1 NÃO autorizada`

Só use `APROVADA` se todos os critérios passarem com evidência ao vivo e arquivos reproduzíveis. Não transforme uma declaração anterior, um script ou um relatório antigo em evidência. Não declare sucesso por aproximação.

## Condição de parada

Se qualquer correção exigir alterar produção, publicar/ativar workflow, executar rede/IA/WhatsApp, expor segredo ou fazer mudança estrutural no Supabase, pare e registre o bloqueio. A Etapa 0 só termina quando o relatório final disser `APROVADA — Etapa 1 autorizada` e todos os validadores acima estiverem verdes.
