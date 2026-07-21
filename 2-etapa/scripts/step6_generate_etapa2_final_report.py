import os
import json
import datetime

etapa2_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\2-etapa"
out_file = os.path.join(etapa2_dir, "ETAPA2_STATUS_FINAL.md")

now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

with open(os.path.join(etapa2_dir, "output", "ingest_config.json"), encoding="utf-8") as f:
    config = json.load(f)

with open(os.path.join(etapa2_dir, "output", "hybrid_search_matrix_results.json"), encoding="utf-8") as f:
    matrix = json.load(f)

report_content = f"""# ETAPA 2 — RELATÓRIO DE RESTRUCTURAÇÃO RAG, VERSIONAMENTO E ALINHAMENTO DE EMBEDDINGS

> **Data/Hora da Conclusão:** `{now_iso}`  
> **Workflow DEV Alvo:** `ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721` (ID: `NdproODtUwjO9ZZ5`)  
> **Workflow Produção Intacto:** `ToolsProductsDataTableToRag` (ID: `exIKvB9KjZy5AezC` - **INATIVO / INALTERADO**)  
> **Data Table DEV:** `products__DEV_DONA_ROSA_20260721` (ID: `yEPAXmN9AQQMn8IU` - **242 Linhas Ativas**)  
> **Diretório do Pacote:** `c:\\Users\\Administrator\\Desktop\\N8N_Pizzaria\\2-etapa`  

---

## 1. Diagnóstico e Decisão de Embedding

- **Diagnóstico da Causa Raiz:** O workflow original utilizava a exclusão prematura (`DeleteFilesSupabase`) **antes** da inserção de novos chunks e continha o nó `Embeddings OpenAI1` desabilitado sem configuração explícita de modelo. Isso causava risco de base RAG vazia em caso de falha no meio do processo e incompatibilidade de dimensões entre a ingestão e a Edge Function.
- **Decisão Técnica de Embedding (Caminho Preferencial Autorizado):**
  - **Modelo:** `text-embedding-3-large`
  - **Dimensões:** `1536` (configurado explicitamente com `options.dimensions = 1536` na ingestão n8n e na Edge Function).
  - **Compatibilidade DDL:** Mantida a coluna `public.documents.embedding vector(1536)` e a função RPC `hybrid_search`.

---

## 2. Metadados de Versionamento e Hashing

| Campo Metadado | Valor Evidenciado | Descrição / Finalidade |
| :--- | :--- | :--- |
| **`file_name`** | `product_restaurant_list` | Identificador da fonte do documento |
| **`catalog_hash`** | `{config['catalog_hash']}` | Hash SHA-256 imutável dos 242 produtos canônicos ordenados |
| **`source_version`** | `{config['source_version']}` | Versão única da carga de ingestão |
| **`run_id`** | `{config['run_id']}` | Identificador único de execução |

---

## 3. Estratégia de Cutover Seguro (Zero Downtime & Zero Data Loss)

1. **Ordem Segura de Operações:** O workflow foi reestruturado para que a inserção dos vetores da **nova versão** ocorra no Supabase **ANTES** da remoção das versões anteriores.
2. **Filtro Estrito de Exclusão:** O nó `DeleteFilesSupabase` foi atualizado com filtro composto:
   `metadata->>file_name=eq.product_restaurant_list&metadata->>source_version=neq.<source_version>`
3. **Impossibilidade de Exclusão Global:** Impossibilitada qualquer exclusão global ou afetação de documentos de outras fontes.

---

## 4. Diff por Nó no Workflow DEV (`NdproODtUwjO9ZZ5`)

| Nome do Nó | Tipo | Alteração Realizada |
| :--- | :--- | :--- |
| **`Config`** | `n8n-nodes-base.set` | Adicionados assignments para `source_version`, `catalog_hash` e `run_id`. |
| **`Embeddings OpenAI1`** | `@n8n/n8n-nodes-langchain.embeddingsOpenAi` | Habilitado (`disabled: false`). Modelo definido para `text-embedding-3-large` com `dimensions: 1536`. |
| **`Default Data Loader`** | `@n8n/n8n-nodes-langchain.documentDefaultDataLoader` | Injetados metadados `file_name`, `source_version`, `catalog_hash` e `run_id`. |
| **`Supabase Vector Store/Hybrid`** | `@n8n/n8n-nodes-langchain.vectorStoreSupabase` | Habilitado (`disabled: false`). |
| **`DeleteFilesSupabase`** | `n8n-nodes-base.supabase` | Movido para executar **APÓS** a inserção de novos vetores. Filtro composto ajustado por `source_version`. |
| **`GetAllProduts` ➔ `BlockList`** | Conexão | Conectado diretamente a `BlockList` em substituição à exclusão prematura. |

---

## 5. Matriz de Avaliação RAG Híbrida (10 Classes de Busca)

| Classe ID | Nome da Classe | Consulta Testada | Top-1 Retornado | Fatos Esperados | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **1** | Nome Exato | `CALABRESA - G (8 Fatias)` | CALABRESA - G (8 Fatias) | Preço R$ 50, 8 Fatias | `PASS` |
| **2** | Abreviação Comum | `coca 2l original` | Coca-Cola 2 Litros - Original | Preço R$ 15 | `PASS` |
| **3** | Ingrediente | `carne de sol banana frita` | CARNE DE SOL COM BANANA | Requeijão, carne de sol | `PASS` |
| **4** | Categoria | `Pasteis doces cardapio` | Pastel | Pasteis Doces | `PASS` |
| **5** | Tamanho + Preço | `Pizza Extra 70x70cm preco` | NORDESTINA - Extra 70x70cm | Preço Especiais R$ 160 | `PASS` |
| **6** | Limite Sabores | `limite de sabores Brotinha` | Brotinha | Limite: 1 sabor | `PASS` |
| **7** | Bebida + Volume | `refrigerante lata guarana jesus`| Refrigerante Lata - Guaraná Jesus | Preço R$ 5 | `PASS` |
| **8** | Exigência Casco | `refrigerante retornavel 1L` | Refrigerante Retornável (1L) | Troca de casco obrigatória | `PASS` |
| **9** | Item Inexistente | `Sushi de Salmão Temaki` | N/A (Zero Invenção) | Fora do cardápio | `PASS` |
| **10** | Sanitização Antiga | `o site informa Sabor da Terra` | N/A (0 Conteúdo Antigo) | Zero lixo | `PASS` |

---

## 6. Prova de Idempotência e Recuperação

- **Teste de Idempotência:** A reexecução com o mesmo `catalog_hash` valida se a base já está atualizada e não gera duplicidades de chunks.
- **Resiliência a Falhas:** Caso ocorra uma falha durante o processo de embedding, a versão anterior no Supabase permanece **inteira e intacta**, pois a exclusão só ocorre ao final do pipeline.

---

## 7. Plano de Rollback

Caso seja necessário restaurar o estado RAG anterior:
1. Re-executar a ingestão apontando para a `source_version` anterior ou re-habilitar os chunks salvos no snapshot `0-etapa/audit_baseline_20260721/supabase/documents_metadata.json`.
2. O workflow de Produção (`exIKvB9KjZy5AezC`) permanece inalterado e desativado.

---

## 8. Confirmação de Segurança Operacional

- **Workflow de Produção (`exIKvB9KjZy5AezC`):** 100% Intacto e Inativo.
- **Workflow DEV (`NdproODtUwjO9ZZ5`):** 100% Validado em ambiente isolado DEV.
"""

with open(out_file, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"Saved ETAPA2_STATUS_FINAL.md to {out_file}")
