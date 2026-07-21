# ETAPA 0 — REVISÃO DE AUDITORIA

> **Revisão live:** `2026-07-21T21:35:36Z`  
> **Instância:** n8n `https://n8n-donarosa.nivanostudio.com.br`  
> **Supabase:** projeto `qucikffpvnvzaxfyugwi`

## Decisão

```text
PENDENTE — Etapa 1 NÃO autorizada
```

## O que passou

- Os três workflows de produção conferem com os backups quanto a nome, ID, estado, 10/16/85 nós, 8/13/69 conexões e IDs de nós.
- Os três workflows DEV existem com os IDs esperados, `active=false`, `availableInMCP=true`, zero triggers e zero nós externos classificados habilitados.
- As três Data Tables DEV existem no projeto `mNx2JLqnsOgn6t6X` com os schemas esperados.
- O catálogo da Etapa 1 tem 242 linhas, distribuição 112/56/32/10/10/22, chave `name` sem duplicidade, preços parseáveis e zero segredo detectado no pacote.
- O rollback descartável está documentado.

## Bloqueios objetivos

1. **Violação de escopo do Prompt 0:** o relatório anterior registra a aplicação de uma migração estrutural no Supabase (`match_documents` e alteração de `hybrid_search`). O Prompt 0 exige somente leitura/introspecção e determina parada quando houver necessidade de mudança estrutural no Supabase. A migração está live, mas não pode ser considerada uma conclusão fiel da Etapa 0.
2. **Evidência da Data Table inconsistente:** `extra_rows_deactivation_log.json` registra 13 linhas inativas e 243 ativas; o relatório final declara 14 inativas e 242 ativas; a prova de idempotência só comprova contagem total 256 e ausência de divergência, não comprova a contagem final por `active`.
3. **Autorização não auditável:** o log declara `deactivated_requested_by_user=true`, mas o ZIP não contém a confirmação explícita que o Prompt 1 exige antes de desativar/excluir extras.
4. **Manifesto incompleto para a Etapa 1:** o checksum existente cobre apenas `0-etapa`; não há manifest reproduzível próprio da Etapa 1.

## Ações feitas nesta revisão

- Não alterei workflows, Data Tables ou Supabase live durante esta auditoria.
- Corrigi apenas o pacote local: as 25 descrições `Extra 70x70cm` voltaram a conter a dimensão oficial; o diff foi recalculado e deixou de classificar essas linhas como `NEW_UNMATCHED`.
- Preservei os relatórios anteriores em `ETAPA0_STATUS_PRIOR_APPROVAL.md` e `1-etapa/ETAPA1_STATUS_PRIOR.md` para rastreabilidade.

## O que você precisa fazer para liberar

- Confirmar explicitamente se a desativação dos extras na Data Table DEV foi autorizada.
- Fornecer/permitir uma leitura/exportação das linhas atuais da Data Table DEV para comprovar: total 256, 242 ativas canônicas e 14 inativas, sem outras ativas.
- Decidir se a migração RAG do Supabase deve permanecer. Se a regra “Supabase somente leitura na Etapa 0” for absoluta, ela precisa ser revertida em uma janela autorizada; não fiz essa reversão porque pode quebrar o workflow RAG de produção.

Até esses pontos serem resolvidos, a Etapa 1 não deve avançar para RAG, produção ou alterações adicionais.
