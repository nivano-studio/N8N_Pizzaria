# Relatório Final de Conclusão da Etapa 0 — Baseline, Isolamento DEV, Segurança e Rollback

> **Data da Conclusão:** 21 de Julho de 2026  
> **Instância n8n Live:** `https://n8n-donarosa.nivanostudio.com.br`  
> **Versão Confirmada ao Vivo:** `2.65.1` (Ambiente Self-Hosted)  
> **Projeto n8n:** `Felipe Viana <vianafelipe509@gmail.com>` (ID: `mNx2JLqnsOgn6t6X`)  
> **Diretório do Pacote:** `c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\`  

---

## 1. Confirmação do Ambiente e Instância n8n Live

| Parâmetro | Evidência Obtida ao Vivo | Status |
| :--- | :--- | :---: |
| **URL n8n API** | `https://n8n-donarosa.nivanostudio.com.br` | **ONLINE** |
| **Saúde da API (`n8n_health_check`)** | Resposta HTTP 200 OK (Latência 977ms) | **SAUDÁVEL** |
| **Versão Reportada** | `2.65.1` | **CONFIRMADA** |
| **Ferramentas MCP Ativas** | 21 ferramentas (7 docs + 14 management) | **DISPONÍVEL** |
| **Projeto n8n** | ID `mNx2JLqnsOgn6t6X` | **CONFIRMADO** |

---

## 2. Workflows DEV Confirmados e Isolados no n8n Live

Todos os workflows DEV foram configurados no n8n live com **IDs próprios e únicos**, totalmente independentes da produção, e mantidos rigorosamente inativos (`active: false`):

| Nome do Workflow DEV | ID Exclusivo DEV | Status | `active` | Nós | Conexões | Triggers Neutralizados |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `ImportPdfToTable__DEV_DONA_ROSA_20260721` | `fq4UCwZ6KOOXm0NY` | **ISOLADO** | `false` | 10 | 8 | `On form submission` (`disabled: true`) |
| `ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721` | `NdproODtUwjO9ZZ5` | **ISOLADO** | `false` | 16 | 13 | `Schedule Trigger` (`disabled: true`) |
| `EvolutionDeliveyRagHibridoDataTables-export__DEV_DONA_ROSA_20260721` | `x7L6Z0klfhvqWx1R` | **ISOLADO** | `false` | 85 | 69 | `Webhook` e `chatTrigger` (`disabled: true`) |

> **Workflows de Produção Intactos:**  
> - `ImportPdfToTable` (`vpPp34JIYrReJxM5`) -> Inalterado  
> - `ToolsProductsDataTableToRag` (`exIKvB9KjZy5AezC`) -> Inalterado  
> - `EvolutionDeliveyRagHibridoDataTables-export` (`XCZsECfv1SNrLN80`) -> Inalterado  

---

## 3. Data Tables DEV Isoladas Criadas e Populadas

Foram criadas Data Tables dedicadas ao ambiente DEV, com os mesmos esquemas de produção, garantindo 100% de isolamento de dados:

| Nome da Data Table DEV | ID DEV n8n | Esquema de Colunas | Linhas Copiadas (Snapshot) | Status Isolamento |
| :--- | :--- | :--- | :---: | :---: |
| `products__DEV_DONA_ROSA_20260721` | `yEPAXmN9AQQMn8IU` | `name`, `description`, `price`, `category`, `image_url`, `active` | **242** | **100% ISOLADO** |
| `customers__DEV_DONA_ROSA_20260721` | `DacGOSDHaMAFF3Zq` | `phone`, `name`, `busines_id`, `resumo`, `email`, `endereco`, `followup_data`, `customer_name`, `customer_email` | **1** | **100% ISOLADO** |
| `invoices__DEV_DONA_ROSA_20260721` | `0iESK6xkLcCfCNUu` | `customer_name`, `invoice_number`, `phone`, `status`, `description`, `total`, `forma_pagamento` | **2** | **100% ISOLADO** |

> **Data Tables de Produção Intactas:**  
> - `products`: `hICNaSYRSMkjHiTT` (242 linhas)  
> - `customers`: `eXHmu98SYFK7A6zN` (1 linha)  
> - `invoices`: `BaMD12kIM3Y5iQDv` (2 linhas)  

---

## 4. Reconfiguração de Nós e Neutralização de Efeitos Externos

### 4.1. Substituição de Referências de Data Tables
Todas as referências a IDs de Data Tables de produção e IDs antigos de outros projetos foram substituídas nos workflows DEV:
- `Upsert row(s)` & `GetAllProduts` -> Apontam exclusivamente para `yEPAXmN9AQQMn8IU` (`products__DEV_DONA_ROSA_20260721`).
- `CustomerData`, `CustomerData2`, `UpdateCustomer` -> Apontam exclusivamente para `DacGOSDHaMAFF3Zq` (`customers__DEV_DONA_ROSA_20260721`).
- `GetInvoices1`, `GetInvoices2`, `UpdateAddInvoice`, `UpdateAddRascunho` -> Apontam exclusivamente para `0iESK6xkLcCfCNUu` (`invoices__DEV_DONA_ROSA_20260721`).

**Resultado do Auditor de Isolamento:**  
`0` referências às Data Tables de produção (`hICNaSYRSMkjHiTT`, `eXHmu98SYFK7A6zN`, `BaMD12kIM3Y5iQDv`) encontradas nos workflows DEV.

### 4.2. Neutralização de Serviços e APIs Externas
Em todas as cópias DEV, os nós que consomem ou disparam serviços externos foram configurados com `disabled: true` e URLs redirecionadas para o stub local seguro `http://127.0.0.1:9999/disabled_dev_stub`:
- **Triggers:** Webhook, Chat Trigger, Form Trigger, Schedule Trigger (`disabled: true`).
- **Comunicação & Mensageria:** Evolution API, `SendWhatsappMsg`, `ElevenLabsGenerateVoice` (`disabled: true` + URL Stubbed).
- **IA & Busca Vectorial:** OpenAI (`gpt-4.1-mini`), OpenAI Embeddings, Supabase Vector Store (`match_documents`), Edge Function `search_restaurante_data` (`disabled: true` + URL Stubbed).
- **Caches Temporários:** Nós Redis (`RemoveFromTrapList`, `AddTrapList`, `BuscaTrapList1`, etc.) desativados.

---

## 5. Redação de Segredos e Sanitização de Credenciais

Todas as chaves estáticas, tokens de API e segredos presentes nos arquivos JSON de backup, exportações DEV e relatórios foram sanitizados e substituídos pelo marcador `[REDACTED_SECRET]`.

- **Credenciais Sanitizadas nos Arquivos:** OpenAI API Keys (`sk-...`), ElevenLabs Keys, Supabase Service Role Keys.
- **Recomendação de Rotação:** As credenciais ativas do ambiente de produção registradas no n8n continuam gerenciadas com segurança pelo cofre interno do n8n via IDs de credencial (`2qdiJ9T6Vo8DpIMI`, `2ryqvQ3GSZue40Nu`, `suQdsHsEoVjlixfK`). Recomenda-se a rotação periódica das chaves no painel do provedor por boas práticas de segurança.

---

## 6. Teste de Rollback em Cópia Descartável

A operacionalidade do procedimento de rollback foi comprovada através de um teste automatizado completo:
1. **Restauração:** Um workflow temporário descartável (`ROLLBACK_TEST_DISPOSABLE_20260721`) foi instanciado no n8n live a partir do arquivo de backup `EvolutionDeliveyRagHibridoDataTables-export_XCZsECfv1SNrLN80_backup.json`.
2. **Validação de Topologia:** O workflow restaurado foi inspecionado via API:
   - Contagem de nós: **85 nós** (100% equivalente).
   - Contagem de conexões: **69 alvos de conexão** (100% equivalente).
3. **Limpeza Automatizada:** O workflow descartável foi deletado (`qJwXD4SWB0gBb44A`) imediatamente após a confirmação.

---

## 7. Tabela de Checksums SHA-256 Registrada

Todos os arquivos da Etapa 0 estão catalogados no arquivo `0-etapa/audit_baseline_20260721/checksums.sha256`:

```text
920b0823a279e6fe7fe1ef885adaf0068cbca1be860796dc84d36a29dde44bb2  .csv/customers.csv
c7c034dd5367baeba7a277789dd1412e2e9c56a8badf586b8390dbe6dce8a71d  .csv/documents_rows.csv
9be234ff25b4e3d94aa17df78ae99674d225ef5d87c2e45e17ace28eb41e5472  .csv/invoices.csv
02b7b1e67e16b2330c71f0c830bafd3173e50051e632a65cb6905eab1ae64049  .csv/products.csv
85d53884a7da858fbddc0eb8f54ddbdf5b0897caddd327d883d02857b77aaa50  .md/Pacote_Prompts_Antigravity_Pizzaria_Dona_Rosa.md
44bc72456403aaf16aae666388db3f188f75de1811d905104bbdf3c43762e55f  .md/cardapio-dona-rosa.md
f4586a1dd3751c31dc663aca22427465cc31c5151206138325421439e43c7a4e  .md/informacoes-pizzaria-dona-rosa copy.md
c3e0253ce281e1d4a1f1ece51fa9ba9f05b51113fbe9c8d5f3b7e6bc8c37ae62  .md/informacoes-pizzaria-dona-rosa.md
190aea794d20f2293b2a6397b73c247cdeee0c57eecf959572f84ddebb3e264b  0-etapa/audit_baseline_20260721/backups/EvolutionDeliveyRagHibridoDataTables-export_XCZsECfv1SNrLN80_backup.json
2d1fa78a744298007ebc0b77ecd8063fcd8a049b50c6ce79c2049a29dacb78bf  0-etapa/audit_baseline_20260721/backups/ImportPdfToTable_vpPp34JIYrReJxM5_backup.json
da9088c021e9ef77322759fc30a79627f2eef375d17f89f64aab13ef7a1babef  0-etapa/audit_baseline_20260721/backups/ToolsProductsDataTableToRag_exIKvB9KjZy5AezC_backup.json
31018de2e883d7b7715b3cbc617d73b69869110568aa271b4c8b644cb6ed2d01  0-etapa/audit_baseline_20260721/datatables_snapshots/customers_eXHmu98SYFK7A6zN_snapshot.json
d7e698b56ffd97065de08ab022c9d1022647c24fd2bc6929e2c3d768a28ab593  0-etapa/audit_baseline_20260721/datatables_snapshots/invoices_BaMD12kIM3Y5iQDv_snapshot.json
4228795cb31889b5c34f77ad23fe9015a8ef178b01294aa0646de43019b3b98e  0-etapa/audit_baseline_20260721/datatables_snapshots/products_hICNaSYRSMkjHiTT_snapshot.json
1298e73b1efe0a910c846a5a04536dfb4338b7e561bbe14aedf5a127144a59b0  0-etapa/audit_baseline_20260721/dev_copies/EvolutionDeliveyRagHibridoDataTables-export__DEV_DONA_ROSA_20260721.json
26a35b866599dfbce8448cfaef773166247b0b347d20da8595ea4e2959881e76  0-etapa/audit_baseline_20260721/dev_copies/ImportPdfToTable__DEV_DONA_ROSA_20260721.json
a32dac40a5c10c020983ce01f0f65eab2a27cc7e7f4f8b8acc9c0c54d13b5f5d  0-etapa/audit_baseline_20260721/dev_copies/ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721.json
44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a  0-etapa/audit_baseline_20260721/dev_datatables_meta.json
a3a6b1bdcc9b3aa2eaf18ee27f5e18e3f922c0c2a1d389ce03fcbe1f463a1be3  0-etapa/baseline_report.md
6239e2c57ab587f075cb7a5b3b4e5e9a0b8aa8bde0991211ee842980fc64e463  hybrid-search/index.ts
```

---

## 8. Checklist de Conclusão da Etapa 0 (Critérios 1 a 10)

- [x] **1. Workflows DEV confirmados ao vivo no n8n** (`fq4UCwZ6KOOXm0NY`, `NdproODtUwjO9ZZ5`, `x7L6Z0klfhvqWx1R`).
- [x] **2. Workflows DEV com IDs próprios e únicos**, totalmente separados da produção.
- [x] **3. Cópias DEV incapazes de alterar produção** (0 referências a Data Tables de produção, todos os nós de envio/escrita desativados/stubbed).
- [x] **4. Data Tables DEV isoladas criadas e populadas** (`yEPAXmN9AQQMn8IU`, `DacGOSDHaMAFF3Zq`, `0iESK6xkLcCfCNUu`).
- [x] **5. Backups e exports legíveis e verificáveis** salvos nos diretórios locais.
- [x] **6. Nenhum segredo exposto** (todos os tokens e chaves redigidos com `[REDACTED_SECRET]`).
- [x] **7. Rollback testado e aprovado em cópia descartável** com 100% de fidelidade de topologia.
- [x] **8. Checksums SHA-256 gerados e auditáveis** no pacote `0-etapa`.
- [x] **9. DDL/Esquema do Supabase documentado** (`documents` schema, RPC `hybrid_search`, OpenAI `text-embedding-3-large` 1536 dim).
- [x] **10. NENHUMA alteração em produção realizada** (produção mantida 100% intacta).

---

> **Aprovação Final da Etapa 0:**  
> A Etapa 0 está **OFICIALMENTE FINALIZADA** e aprovada. O ambiente de desenvolvimento está completamente isolado, protegido e pronto para o início da Etapa 1.
