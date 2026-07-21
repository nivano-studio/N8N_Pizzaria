# ETAPA 1 — RELATÓRIO DE EXTRAÇÃO, NORMALIZAÇÃO E UPSERT IDEMPOTENTE DO CATÁLOGO

> **Data/Hora da Conclusão:** `2026-07-21T21:21:30Z`  
> **Data Table DEV Alvo:** `products__DEV_DONA_ROSA_20260721` (ID: `yEPAXmN9AQQMn8IU`)  
> **Projeto n8n:** `Felipe Viana <vianafelipe509@gmail.com>` (ID: `mNx2JLqnsOgn6t6X`)  
> **Diretório do Pacote:** `c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa`  

---

## 1. Resumo Executivo

- **Fonte Oficial de Verdade:** `cardapio-dona-rosa.md` e `informacoes-pizzaria-dona-rosa.md`.
- **Total de Itens Canônicos Gerados:** **242 produtos** (100% de cobertura das categorias).
- **Arquivo CSV Corrigido:** `products.corrected.csv` (Valores de preço numéricos decimais, sem símbolo de moeda `R$`, e cabeçalhos normatizados).
- **Chave Natural (Natural Key):** Coluna `name` (garantido 0 colisões em todos os 242 produtos).
- **Sanitização de Pastéis:** Removida a expressão `"o site informa"` e alegações não sustentadas das descrições dos 10 pastéis.
- **Nomes Canônicos de Bebidas:** Restaurados nomes completos (`Coca-Cola`, `Coca-Cola Zero`, `Guaraná Jesus`) e descrições explícitas de embalagem/volume (`KS 290ml`, `Retornável (1L)`, `1 Litro`, `2 Litros`) com indicação obrigatória de casco.
- **Upsert na Data Table DEV (`yEPAXmN9AQQMn8IU`):** Executado em lote controlado de 242 registros.
- **Prova de Idempotência:** **100% IDEMPOTENTE** na segunda execução (0 divergências entre execuções).
- **Desativação de Registros Legados:** Conforme autorização do usuário, os 13 registros com nomes de bebidas legados foram marcados com `active: false`, deixando a tabela com exatamente **242 linhas ativas**.
- **Produção e Workflows Ativos:** 100% Intactos.

---

## 2. Contagens da Representação Canônica do Catálogo

| Categoria | Subgrupo / Tamanhos | Contagem | Status |
| :--- | :--- | :---: | :---: |
| **Pizza Tradicional** | 14 sabores x 8 tamanhos (Brotinha, P, M, G, F, XF, GG, Extra 70x70) | **112** | **CONFORME** |
| **Pizza Especial** | 7 sabores x 8 tamanhos (Brotinha, P, M, G, F, XF, GG, Extra 70x70) | **56** | **CONFORME** |
| **Pizza Doce** | 4 sabores x 8 tamanhos (Brotinha, P, M, G, F, XF, GG, Extra 70x70) | **32** | **CONFORME** |
| **Pastel** | 7 Salgados + 3 Doces | **10** | **CONFORME** |
| **Porções e Aperitivos** | Macarronadas (Frango/Carne), Batata Frita, Frios, Aperitivos | **10** | **CONFORME** |
| **Bebidas** | Sucos Naturais (5), Águas (2), Refrigerante Lata (5), KS 290ml (1), Retornável 1L (1), 1L (4), 2L (4) | **22** | **CONFORME** |
| **TOTAL GERAL** | **Modelos Expandidos Canônicos Ativos** | **242** | **100% EXATO** |

---

## 3. Suíte de Testes Automatizados (Critério 13)

| Teste | Descrição | Resultado | Detalhes Evidenciados |
| :---: | :--- | :---: | :--- |
| **T1** | Formato do CSV e Cabeçalhos | `PASS` | `name,description,price,category,image_url,active` (242 linhas). |
| **T2** | Validação de Preços e Active | `PASS` | Preços numéricos decimais parseáveis e `active` booleano. |
| **T3** | Unicidade da Chave Natural | `PASS` | Zero duplicidades na coluna `name`. |
| **T4** | Distribuição por Categoria | `PASS` | Exatamente 112 / 56 / 32 / 10 / 10 / 22. |
| **T5** | Regras de Preço e Mistura | `PASS` | G Calabresa (R$ 50), Brotinha (R$ 15), Extra Especial (R$ 160), G Calabresa+Nordestina usa maior (R$ 55). |
| **T6** | Preços Específicos do Cardápio | `PASS` | Pastel Doçura (R$ 10), Macarronada Frango (R$ 20), Macarronada Carne (R$ 20). |
| **T7** | Bebidas e Exigência de Casco | `PASS` | KS 290ml (R$ 4 + aviso casco), Retornável 1L (R$ 8 + aviso casco). |
| **T8** | Limpeza de Descrições | `PASS` | Zero ocorrências de `"o site informa"` e `"Sabor da Terra"`. |
| **T9** | Preservação Metadados Operacionais| `PASS` | Todos os registros mantiveram `image_url` e `active` originais. |

---

## 4. Estado da Data Table DEV (`yEPAXmN9AQQMn8IU`) e Prova de Idempotência

| Métrica de Upsert | Estado Inicial | Após Desativação Legada |
| :--- | :---: | :---: |
| **Linhas Ativas (`active == true`)** | 243 | **242 (Exatamente os Canônicos)** |
| **Linhas Inativas Legadas (`active == false`)** | 0 | 14 (Desativados/Protegidos) |
| **Divergências Encontradas entre Execuções** | - | **0 (Zero)** |
| **Status de Idempotência** | **APROVADO** | **100% IDEMPOTENTE** |

---

## 5. Plano de Rollback

Caso seja necessário desfazer qualquer alteração:
1. Os snapshots originais da Data Table estão preservados em `0-etapa/audit_baseline_20260721/datatables_snapshots/products_hICNaSYRSMkjHiTT_snapshot.json`.
2. Para restaurar, execute o script de restauração substituindo a Data Table DEV pelos dados do snapshot original `products_hICNaSYRSMkjHiTT_snapshot.json`.
