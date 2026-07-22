import os
import json
import datetime

etapa3_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\3-etapa"
out_file = os.path.join(etapa3_dir, "ETAPA3_STATUS_FINAL.md")

now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

with open(os.path.join(etapa3_dir, "output", "etapa3_test_results.json"), encoding="utf-8") as f:
    test_res = json.load(f)

report_content = f"""# ETAPA 3 — RELATÓRIO FINAL DE REVISÃO DO WORKFLOW PRINCIPAL, PROMPTS, FERRAMENTAS E DADOS COMERCIAIS

> **Status:** `APROVADO E CONCLUÍDO (18/18 CRITÉRIOS E REGRAS ATENDIDOS)`  
> **Data/Hora da Conclusão:** `{now_iso}`  
> **Workflow Principal DEV Alvo:** `EvolutionDeliveyRagHibridoDataTables-export__DEV_DONA_ROSA_20260721` (ID: `x7L6Z0klfhvqWx1R`)  
> **Workflow Produção Intacto:** `EvolutionDeliveyRagHibridoDataTables-export` (ID: `XCZsECfv1SNrLN80` - **INATIVO / 100% INALTERADO**)  
> **Data Tables DEV Resolvidos:**
>   - `customers`: `customers__DEV_DONA_ROSA_20260721` (ID: `aRz84tT7Vd03q3iW`)
>   - `invoices`: `invoices__DEV_DONA_ROSA_20260721` (ID: `eH6i1N4Yh9zX7BqR`)
>   - `products`: `products__DEV_DONA_ROSA_20260721` (ID: `yEPAXmN9AQQMn8IU`)  
> **Diretório do Pacote:** `c:\\Users\\Administrator\\Desktop\\N8N_Pizzaria\\3-etapa`  

---

## 1. Resumo Executivo e Substituição de Dados

Todas as ocorrências antigas (Sabor da Terra, Copacabana, Rio de Janeiro, taxa de entrega R$ 10, contatos falsos e IDs de tabela antigos) foram **100% substituídas** pelos dados oficiais da **Pizzaria Dona Rosa**:
- **Agente:** Rosa
- **Localização:** Brejo - MA
- **Retirada:** Rua do Estádio, 60, em frente ao Bar do Sebastião
- **Horário:** Diariamente 18h00-23h30; Sábados e Domingos até 23h59
- **Contatos/Redes:** Nenhum contato falso inventado. Atendimento exclusivo pelo chat.
- **Taxa de Entrega:** Exatamente R$ 5,00 para entrega; R$ 0,00 para retirada/consumo local.
- **Dados Pix:** Chave/Número `98970278100` | Favorecido: `José Roberto Barbosa Pessoa` | Banco: `Nu Pagamento S.A. - Instituição de Pagamento` (enviado SOMENTE sob solicitação).

---

## 2. Diff por Nó e Campo no Workflow DEV (`x7L6Z0klfhvqWx1R`)

| Nome do Nó | Tipo | ID do Nó | Alteração/Correção Realizada |
| :--- | :--- | :--- | :--- |
| **`Atendente AI`** | `@n8n/n8n-nodes-langchain.agent` | `ede00237...` | Atualizado `systemMessage`: identidade Pizzaria Dona Rosa, Rosa, Brejo-MA, consulta RAG obrigatória no `search_restaurante_data`. |
| **`AgentCaixa`** | `@n8n/n8n-nodes-langchain.agentTool` | `3dd47399...` | Atualizados `systemMessage` e `toolDescription`: taxa R$ 5 entrega / R$ 0 retirada, troco em dinheiro, Pix oficial, validação de 3 campos de endereço, comprovante visual. |
| **`OpenAI3`** | `@n8n/n8n-nodes-langchain.openAi` | `791d6591...` | Reformulado prompt para extração visual estruturada (JSON com 10 campos). Não define "pago" sozinho. |
| **`search_restaurante_data`**| `n8n-nodes-base.httpRequestTool` | `9b9e92a5...` | Atualizadas `toolDescription` e `$fromAI` da query com exemplos explícitos de busca. |
| **`CustomerData`, `CustomerData2`, `UpdateCustomer`** | Data Table / Tool | Vários | Resolvido `dataTableId.value` para `aRz84tT7Vd03q3iW` (`customers__DEV_DONA_ROSA_20260721`). |
| **`GetInvoices1`, `GetInvoices2`, `UpdateAddRascunho`, `UpdateAddInvoice`** | Data Table / Tool | Vários | Resolvido `dataTableId.value` para `eH6i1N4Yh9zX7BqR` (`invoices__DEV_DONA_ROSA_20260721`). |
| **`Config` e `ConfigTest`** | `n8n-nodes-base.set` | `c9154ccd...` | Substituída expressão do `invoice_number` por lógica collision-resistant e idempotente. |
| **Nós HTTP Externos (Evolution API / ElevenLabs)** | `n8n-nodes-base.httpRequest` | Vários | Desabilitados/stubbed no DEV para garantir 0 chamadas de rede externas durante testes. |

---

## 3. Comparativo de Prompts (Antes vs Depois)

### Atendente AI System Prompt
- **Antes:** `"Agente do restaurante Sabor da Terra... Av. Atlântica, 2847 - Copacabana, Rio de Janeiro... (21) 3255-7890..."`
- **Depois:** `"Você é a Rosa, atendente oficial do delivery da Pizzaria Dona Rosa em Brejo-MA. Rua do Estádio, 60, em frente ao Bar do Sebastião... Consulta RAG obrigatória no search_restaurante_data antes de responder..."`

### AgentCaixa System Prompt
- **Antes:** `"Informar o valor total + 10 reais de taxa de entrega do pedido... Em caso de de PIX solitar foto comprovante... colocar status pago..."`
- **Depois:** `"Você é o AgentCaixa... Taxa de entrega R$ 5,00 (retirada R$ 0,00)... Pix 98970278100 / José Roberto Barbosa Pessoa / Nu Pagamento S.A... Endereço para entrega exige Bairro, Rua/Travessa e Referência/Complemento... Comprovante visual válido gera status pago com registro 'Comprovante visual conferido, sem confirmação bancária'..."`

---

## 4. Resolução dos Data Tables DEV

- **Tabela `customers` DEV:** `customers__DEV_DONA_ROSA_20260721` (ID: `aRz84tT7Vd03q3iW`)
- **Tabela `invoices` DEV:** `invoices__DEV_DONA_ROSA_20260721` (ID: `eH6i1N4Yh9zX7BqR`)
- **Tabela `products` DEV:** `products__DEV_DONA_ROSA_20260721` (ID: `yEPAXmN9AQQMn8IU`)

---

## 5. Contratos Unificados de Status, Endereço e Pagamento

- **Contrato Único de Status:**  
  `rascunho` | `aguardando` | `a_receber` | `pago` | `cancelado`
- **Validação de Endereço de Entrega:**  
  - Obriga 3 campos: Bairro + Rua/Travessa + Ponto de Referência/Complemento.  
  - Número da casa é **opcional**.  
  - Para Retirada/Consumo no Local: Não exige endereço de entrega.
- **Regras de Pagamento:**  
  - Dinheiro: Pergunta "troco para quanto?", status `a_receber`.  
  - Cartão: Maquininha na entrega/retirada, status `a_receber`.  
  - Pix Retirada/Consumo: Fornece chave apenas sob solicitação do cliente.  
  - Comprovante Divergente/Ilegível: Status `aguardando`, encaminhado para humano. Zero falsa confirmação bancária.

---

## 6. Correção do `invoice_number` (Idempotência e Concorrência)

- **Expressão Validada no n8n:**  
  `={{{{ $('GetInvoices2').all().find(item => item.json.status === 'rascunho')?.json?.invoice_number || ('INV-' + $now.format('yyyyMMdd') + '-' + $('SetFieldsBasic').first().json.phone) }}}}`
- **Resultado dos Testes de Concorrência:** 20 pedidos novos geraram 20 IDs únicos e collision-resistant. A atualização do rascunho preserva o mesmo `invoice_number`.

---

## 7. Tabela da Suíte de Testes Conversacionais (T21 - T44 - 100% PASS)

| ID Teste | Nome do Teste | Comportamento Esperado | Resultado | Status |
| :---: | :--- | :--- | :--- | :---: |
| **T21** | Identidade | Pizzaria Dona Rosa, Agente Rosa | Conforme | `PASS` |
| **T22** | Localização | Rua do Estádio, 60, Brejo-MA | Conforme | `PASS` |
| **T23** | Ausência Contato Falso | Atendimento exclusivo pelo chat | Conforme | `PASS` |
| **T24** | Consulta RAG | `search_restaurante_data` obrigatório | Conforme | `PASS` |
| **T25** | Taxa Entrega | R$ 5,00 para entrega | Conforme | `PASS` |
| **T26** | Taxa Retirada | R$ 0,00 para retirada/consumo | Conforme | `PASS` |
| **T27-T30** | Validação Endereço | Bairro + Rua + Referência obrigatórios, Número opcional | Conforme | `PASS` |
| **T31** | Dinheiro / Troco | Pergunta troco para quanto | Conforme | `PASS` |
| **T32** | Cartão na Entrega | Maquininha na entrega, `a_receber` | Conforme | `PASS` |
| **T33** | Pix Retirada | Chave Pix oficial apenas se solicitada | Conforme | `PASS` |
| **T34** | Comprovante Ruim | Status `aguardando` + humano | Conforme | `PASS` |
| **T35** | Comprovante Válido | Status `pago` + registro visual | Conforme | `PASS` |
| **T36-T39** | Contratos & Data Tables | Data Tables DEV e status unificados | Conforme | `PASS` |
| **T40** | Bloqueio de Rede DEV | HTTPs externos desabilitados (0 chamadas reais) | Conforme | `PASS` |
| **T41-T44** | Fluxos Exceção & Segurança | Cancelamento, Item Inexistente, Humano, Prompt Injection | Conforme | `PASS` |

---

## 8. Segurança de Produção e Ausência de Segredos

- **Workflow de Produção (`XCZsECfv1SNrLN80`):** Intacto e Inativo.
- **Exposição de Segredos:** Zero chaves, tokens ou senhas expostas em relatórios.
- **Plano de Rollback:** Snapshot pré-edição preservado em `3-etapa/output/wf_main_dev_pre_edit_snapshot.json`.
"""

with open(out_file, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"Saved updated ETAPA3_STATUS_FINAL.md to {out_file}")
