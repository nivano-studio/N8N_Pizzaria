# Pacote de Prompts para Correção Auditável - Pizzaria Dona Rosa

## Diagnóstico consolidado

| Componente                                  | Evidência                                                                                                                                                                                                                                                                                                                                                                                                                                          | Problema                                                                                                                                                 | Gravidade                           | Fonte                                                                        | Impacto                                                                                        | Prompt que tratará o problema             |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------ |
| Baseline dos workflows                      | Os três fluxos foram localizados ao vivo.`ImportPdfToTable`: ID `vpPp34JIYrReJxM5`, ativo, versão de rascunho `a0c5c3b5-9d6f-42f0-b26a-d2fb0bcc8de7`, versão ativa `0dde7c8c-be1a-49b9-a440-14bcdb6d6c9b`. `ToolsProductsDataTableToRag`: ID `exIKvB9KjZy5AezC`, inativo, versão `da54d7b7-a3ca-4a4b-a8ef-a7ddd1b4eda5`. Fluxo principal: ID `XCZsECfv1SNrLN80`, ativo, versão ativa `8e3a75f9-38ce-4e56-a1bf-ffddefafe260`. | Ainda não existem, no material entregue, backups externos verificáveis, cópias de desenvolvimento e plano de rollback testado.                        | Crítica                            | MCP n8n ao vivo                                                              | Qualquer alteração direta pode comprometer produção e dificultar restauração.            | Prompt 0                                   |
| Catálogo e Data Table`products`          | `products.csv` possui 242 registros e coincide campo a campo com os 242 itens lidos na execução `1104` do Data Table ao vivo `products` (`hICNaSYRSMkjHiTT`). Distribuição: 112 tradicionais, 56 especiais, 32 doces, 10 pastéis, 10 porções/aperitivos e 22 bebidas.                                                                                                                                                                | A estrutura e as contagens estão coerentes, mas o conteúdo ainda contém fatos/redações não sustentados e nomes não canônicos.                    | Alta                                | `products.csv`, execução `1104`, Data Table ao vivo, cardápio oficial | Erros são propagados integralmente para o RAG.                                                | Prompt 1                                   |
| Descrições dos pastéis                   | Os 10 pastéis possuem a redação “o site informa”, ausente da fonte oficial; quatro chunks exportados em`documents_rows.csv` ainda contêm essa redação.                                                                                                                                                                                                                                                                                    | Conteúdo não oficial e desnecessário foi incorporado ao catálogo pesquisável.                                                                       | Alta                                | `products.csv`, `documents_rows.csv`, `cardapio-dona-rosa.md`          | O agente pode citar uma fonte inexistente e devolver explicações inventadas.                 | Prompts 1 e 2                              |
| Bebidas                                     | Há abreviações como`KS - Coca`, `Refrigerante Retornável - Coca`, `Refrigerante 1L - Jesus` e `Refrigerante 2L - Jesus`, enquanto a fonte oficial usa nomes completos, incluindo Coca-Cola, Guaraná Jesus, 290 ml, 1 litro e 2 litros.                                                                                                                                                                                                 | Nomes e volumes não estão totalmente canônicos.                                                                                                       | Alta                                | `products.csv` versus `cardapio-dona-rosa.md`                            | Busca exata, busca por marca/volume e respostas do agente podem perder precisão.              | Prompt 1                                   |
| Tipo de preço                              | Todos os preços do CSV são numericamente válidos e não negativos, porém a coluna`price` do Data Table ao vivo é do tipo `string`.                                                                                                                                                                                                                                                                                                         | Há diferença entre valor semanticamente numérico e armazenamento textual. Uma migração automática poderia quebrar consumidores.                    | Média                              | CSV e esquema MCP da Data Table                                              | Ordenação, filtros, validações e cálculos podem se comportar como texto.                  | Prompts 0 e 1                              |
| Campos operacionais                         | `image_url` e `active` estão preenchidos em todos os 242 registros. O workflow RAG filtra `active=true`, e `ConvertToMarkdown` inclui `image_url` no Markdown.                                                                                                                                                                                                                                                                           | Esses campos são usados e não podem ser apagados; ao mesmo tempo, URLs de imagem não devem poluir o conteúdo recuperável sem benefício comprovado. | Média                              | `products.csv` e workflow RAG ao vivo                                      | Exclusão quebra disponibilidade/imagens; inclusão indiscriminada reduz qualidade dos chunks. | Prompts 1 e 2                              |
| Indexação RAG                             | A execução`1104` leu 242 produtos, removeu 120 documentos da própria fonte e inseriu 120 chunks. O fluxo executa `DeleteFilesSupabase` antes da nova inserção.                                                                                                                                                                                                                                                                             | A sincronização abre uma janela de perda total do índice se a geração ou inserção falhar após o delete.                                          | Crítica                            | Workflow RAG e execução`1104`                                            | O catálogo pode ficar indisponível ou parcialmente indexado.                                 | Prompt 2                                   |
| Idempotência/versionamento do RAG          | Os 120 documentos exportados usam`file_name=product_restaurant_list`, sem hash ou versão de catálogo.                                                                                                                                                                                                                                                                                                                                           | Não há identificação forte da versão, detecção segura de reexecução nem cutover auditável.                                                     | Alta                                | `documents_rows.csv` e workflow RAG                                        | Duplicidade, índice parcial e rollback impreciso.                                             | Prompt 2                                   |
| Modelo de embedding                         | O nó`Embeddings OpenAI1` v1.2 não define `model`; o padrão confirmado para essa versão é `text-embedding-3-small`, 1536 dimensões. A Edge Function usa explicitamente `text-embedding-3-large` com 1536 dimensões. Os 120 vetores exportados têm 1536 posições.                                                                                                                                                                   | Mesma dimensão não significa mesmo espaço vetorial: indexação e consulta usam modelos diferentes.                                                   | Crítica                            | Workflow RAG, definição do nó n8n e`hybrid-search/index.ts`             | A similaridade vetorial perde validade e prejudica o ranking híbrido.                         | Prompt 2                                   |
| DDL e RPC                                   | O ZIP mostra chamada a`hybrid_search(query_text, query_embedding, match_count=10)`, mas não contém o DDL da função, tipo da coluna, índices ou pesos textual/vetorial.                                                                                                                                                                                                                                                                       | Não é possível certificar assinatura, filtros, ranking ou atomicidade somente com o material anexado.                                                 | Bloqueante para mudança estrutural | `hybrid-search.zip`                                                        | Alterações de RPC, tabela, índice ou vetor seriam especulativas.                            | Prompts 0 e 2                              |
| Atendente AI                                | O`systemMessage` ao vivo ainda identifica “Sabor da Terra” e contém endereço em Copacabana/Rio de Janeiro, telefone, WhatsApp, Instagram e horário antigos.                                                                                                                                                                                                                                                                                  | Identidade e dados comerciais estão errados na versão ativa.                                                                                           | Crítica                            | Workflow principal ao vivo                                                   | Atendimento fornece dados de outra empresa.                                                    | Prompt 3                                   |
| AgentCaixa                                  | O prompt ao vivo soma`10 reais` de entrega para todo pedido. A regra oficial é R$ 5 apenas em entrega.                                                                                                                                                                                                                                                                                                                                           | Taxa incorreta e aplicada sem distinguir entrega, retirada e consumo local.                                                                              | Crítica                            | Workflow principal versus`informacoes-pizzaria-dona-rosa.md`               | Cobrança indevida e total incorreto.                                                          | Prompt 3                                   |
| Endereço de entrega                        | `UpdateCustomer` aceita uma única string “Endereço do cliente”; o prompt não exige bairro, rua/travessa e referência/complemento, e não deixa claro que o número é opcional.                                                                                                                                                                                                                                                             | O agente pode finalizar entrega com endereço insuficiente ou exigir indevidamente o número.                                                            | Alta                                | Workflow principal e regra oficial                                           | Falha operacional de entrega.                                                                  | Prompt 3                                   |
| Pagamento e comprovante                     | O AgentCaixa diz que qualquer comprovante recebido deve mudar o status para pago. O analisador de imagem pede valor, data, horário e favorecido, mas não impõe legibilidade, compatibilidade integral, saída estruturada, estado pendente ou distinção entre análise visual e liquidação bancária.                                                                                                                                        | Confirmação de pagamento excessivamente permissiva.                                                                                                    | Crítica                            | `AgentCaixa`, `OpenAI3` e regra oficial                                  | Fraude, baixa incorreta e alegação enganosa de pagamento confirmado.                         | Prompt 3                                   |
| Ferramenta de busca                         | `search_restaurante_data.toolDescription` é genérica e a descrição do parâmetro `query` está vazia.                                                                                                                                                                                                                                                                                                                                       | O agente não recebe contrato claro de quando usar a busca e como formular consultas.                                                                    | Alta                                | Workflow principal ao vivo                                                   | O agente deixa de consultar o catálogo ou envia consultas vagas.                              | Prompt 3                                   |
| Referências de Data Tables nas ferramentas | As tabelas acessíveis são`customers=eXHmu98SYFK7A6zN`, `invoices=BaMD12kIM3Y5iQDv` e `products=hICNaSYRSMkjHiTT`. Entretanto, `UpdateCustomer` aponta para `AIwE75J1sVmYQjdk`, e `UpdateAddRascunho`/`UpdateAddInvoice` apontam para `XbYdEIzrF5Ltlrll`, IDs não localizados.                                                                                                                                                    | Ferramentas do agente referenciam tabelas antigas/inexistentes.                                                                                          | Crítica                            | MCP Data Tables e workflow principal                                         | Atualizações de cliente, rascunho e pedido podem falhar.                                     | Prompt 3                                   |
| Falha mascarada                             | Na execução`1125`, o workflow terminou com status geral `success`, mas o nó `UpdateAddInvoice` falhou com “Could not find the data table”.                                                                                                                                                                                                                                                                                               | O status global do workflow não comprova que as ferramentas internas funcionaram.                                                                       | Crítica                            | Execução`1125`                                                           | Pedido pode parecer processado sem ter sido gravado.                                           | Prompts 3 e 4                              |
| Contratos de status                         | O AgentCaixa usa`a_receber`; `UpdateAddInvoice` orienta somente `pago`, `aguardando` ou `cancelado`; `UpdateAddRascunho` fixa `rascunho`.                                                                                                                                                                                                                                                                                             | O estado do pedido não possui contrato único e coerente.                                                                                               | Alta                                | Nós do workflow principal                                                   | Transições ambíguas, filtros quebrados e pedidos presos.                                    | Prompt 3                                   |
| Número do pedido                           | `invoice_number` é data + quantidade retornada por `GetInvoices`, que tem limite 10.                                                                                                                                                                                                                                                                                                                                                           | Após dez pedidos do cliente ou em concorrência, o número pode colidir; contar linhas também não é idempotente.                                     | Alta                                | `Config`, `ConfigTest`, `GetInvoices1` e `GetInvoices2`              | Um pedido pode sobrescrever ou misturar outro.                                                 | Prompt 3                                   |
| Segurança de configuração                | O nó HTTP de busca contém uma chave Supabase diretamente em headers, em vez de referência a credencial gerenciada. O valor foi omitido deste relatório.                                                                                                                                                                                                                                                                                         | Segredo/chave operacional fica incorporado à definição do workflow e aos backups.                                                                     | Alta                                | Workflow principal ao vivo                                                   | Exposição em exportações, histórico e auditoria.                                          | Prompts 0 e 3                              |
| Caminho de notificações                   | `SendWhatsappMsg` é ferramenta do AgentCaixa e faz chamada externa; o número de destino ainda é placeholder.                                                                                                                                                                                                                                                                                                                                   | Testes podem tentar uma chamada real ou falhar sem produzir evidência adequada.                                                                         | Alta                                | Workflow principal ao vivo                                                   | Efeito externo acidental ou falso positivo de teste.                                           | Prompts 0, 3 e 4                           |
| ImportPdfToTable                            | O fluxo ativo usa IA para extrair catálogo, divide texto em três blocos e faz upsert apenas por`name`; `image_url` não é atualizado.                                                                                                                                                                                                                                                                                                        | É uma dependência potencialmente destrutiva se usada como mecanismo de correção canônica, mas não há prova de que precise ser alterada agora.     | Média                              | Workflow`ImportPdfToTable` ao vivo                                         | Reimportação pode recriar nomes diferentes e deixar registros antigos ativos.                | Prompts 0, 1 e 2, apenas como dependência |

## Dependências e bloqueios

- Antes de qualquer mudança estrutural no Supabase, o Antigravity deve obter e arquivar: DDL da tabela `documents`, tipo exato da coluna `embedding`, índices, constraints, DDL completo da RPC `hybrid_search`, permissões e política de rollback. Sem isso, deve parar a parte estrutural do Prompt 2.
- O MCP disponível nesta análise expôs o esquema das Data Tables, mas não uma operação direta de listagem de todas as linhas. A equivalência entre CSV e Data Table foi comprovada pelos 242 itens preservados na execução `1104`; o Antigravity deve repetir a leitura em baseline e não confiar apenas no export.
- A alteração de tipo de `price`, a troca do modelo de embedding, a criação de função transacional, a migração de credenciais e qualquer limpeza ampla exigem aprovação explícita. Correções de dados em cópias de desenvolvimento não exigem nova pergunta.
- Não há bloqueio para gerar ou executar os Prompts 0 e 1 em modo de desenvolvimento. O Prompt 2 deve parar antes de reindexar se modelo, dimensão e DDL não forem confirmados. O Prompt 3 deve parar antes de testar ferramentas se as Data Tables de desenvolvimento não estiverem resolvidas.

## Ordem segura de execução

Os cinco prompts separam preparação, dados, indexação, atendimento e auditoria para impedir que uma correção posterior seja feita sobre uma base ainda errada. O Prompt 0 cria baseline, cópias e rollback. O Prompt 1 corrige a fonte canônica e a Data Table de desenvolvimento. O Prompt 2 só então reindexa o catálogo correto. O Prompt 3 adapta o agente e os contratos das ferramentas. O Prompt 4 assume postura independente de revisão e tenta reprovar a solução com testes de regressão, negativos e de efeitos externos.

## Prompt 0 — Preparação, backup e baseline

```text
# 1. Papel
Atue como arquiteto sênior de n8n, Supabase/RAG, segurança operacional e QA. Use czlonkowski/n8n-mcp e czlonkowski/n8n-skills. Nesta etapa, sua função é criar baseline, backups, cópias de desenvolvimento, matriz de dependências e rollback verificável. Não implemente ainda as correções dos Prompts 1 a 4.

# 2. Objetivo
Garantir que toda mudança futura ocorra em cópias isoladas, com identificação exata das versões, dados e dependências, e que seja possível restaurar o estado anterior sem depender de memória ou suposições.

# 3. Contexto confirmado
- Instância n8n atual: self-hosted 2.29.10, conforme evidência fornecida pelo usuário; confirme ao vivo.
- ImportPdfToTable: ID vpPp34JIYrReJxM5; ativo; rascunho a0c5c3b5-9d6f-42f0-b26a-d2fb0bcc8de7; versão ativa 0dde7c8c-be1a-49b9-a440-14bcdb6d6c9b.
- ToolsProductsDataTableToRag: ID exIKvB9KjZy5AezC; inativo; versão da análise da54d7b7-a3ca-4a4b-a8ef-a7ddd1b4eda5.
- EvolutionDeliveyRagHibridoDataTables-export: ID XCZsECfv1SNrLN80; ativo; versão ativa 8e3a75f9-38ce-4e56-a1bf-ffddefafe260.
- Data Tables acessíveis na análise: products hICNaSYRSMkjHiTT, customers eXHmu98SYFK7A6zN, invoices BaMD12kIM3Y5iQDv. Reconfirme; não copie IDs para outra instância sem resolver por nome/projeto.
- Execução RAG 1104: 242 produtos lidos, 120 documentos removidos da própria fonte e 120 inseridos.
- Execução principal 1125: status global success, mas UpdateAddInvoice falhou no nível do nó. O baseline deve registrar erros internos, não apenas o status global.

# 4. Fontes de verdade, por precedência
1. cardapio-dona-rosa(1).md para catálogo, preços, tamanhos, fatias, ingredientes, bebidas e casco.
2. informacoes-pizzaria-dona-rosa(2).md para empresa, atendimento, entrega, pagamento, Pix, retirada e consumo local.
3. Workflows e Data Tables ao vivo via MCP.
4. products(1).csv.
5. documents_rows(1).csv.
6. hybrid-search(1).zip.
7. customers(1).csv e invoices(1).csv somente como amostras de esquema.
8. ImportPdfToTable apenas como dependência.

# 5. Escopo autorizado
- Ler arquivos, consultar MCP e histórico, obter DDL/esquemas em modo somente leitura, gerar relatórios, fixtures e checksums.
- Exportar backups e criar cópias de desenvolvimento com triggers externos desabilitados.
- Redigir segredos dos relatórios e backups compartilháveis.
- Executar validações locais sem efeitos externos.

# 6. Fora do escopo
- Não alterar, ativar, publicar ou executar produção.
- Não enviar WhatsApp, processar pedido real, chamar webhook de produção ou limpar dados.
- Não mudar credenciais, dependências, modelo de embedding, dimensão, DDL, RPC ou arquitetura.

# 7. Arquivos e workflows envolvidos
Arquivos anexos listados acima; os três workflows identificados; Data Tables products/customers/invoices; tabela Supabase documents; RPC hybrid_search; Edge Function hybrid-search.
Registre SHA-256 dos anexos e compare com este baseline: cardápio 44bc72456403aaf16aae666388db3f188f75de1811d905104bbdf3c43762e55f; informações c3e0253ce281e1d4a1f1ece51fa9ba9f05b51113fbe9c8d5f3b7e6bc8c37ae62; products 02b7b1e67e16b2330c71f0c830bafd3173e50051e632a65cb6905eab1ae64049; documents c7c034dd5367baeba7a277789dd1412e2e9c56a8badf586b8390dbe6dce8a71d; hybrid-search b798cadf5e986aa1d941d7e62a1b50a5189b29dfabf783bb6c74f0228c9d4aa8. Se diferirem, use o arquivo efetivamente presente, registre o novo hash e não finja equivalência.

# 8. Sequência de execução
1. Confirmar instância, projeto, saúde, versão do n8n e capacidades reais das ferramentas; não inventar nomes de operações.
2. Localizar cada workflow por nome e ID; registrar active, versionId, activeVersionId, updatedAt, nós, conexões, triggers e credenciais apenas por tipo/nome redigido.
3. Exportar JSON completo e legível das versões ativa e atual de cada workflow. Calcular hash dos exports.
4. Criar cópias com sufixo __DEV_DONA_ROSA_<data>. Deixar inativas. Neutralizar nas cópias todos os triggers externos, Schedule Trigger, Webhook de produção, Evolution API, SendWhatsappMsg e qualquer HTTP com efeito externo; preserve a configuração original no backup.
5. Exportar esquemas e snapshots controlados das Data Tables. Criar cópias de desenvolvimento sem apagar as originais.
6. Obter, somente leitura, DDL de documents, embedding, índices e hybrid_search; registrar modelo/dimensão da ingestão e da consulta.
7. Produzir matriz nó -> Data Table/RPC/endpoint/credencial/subworkflow -> ambiente -> efeito externo.
8. Registrar contagens por tabela, fonte, versão e status. Redigir PII e segredos.
9. Definir rollback por componente e provar que os backups reabrem e têm nós/conexões esperados.
10. Parar antes de qualquer correção funcional.

# 9. Regras que devem ser preservadas
Preserve nomes/IDs dos nós, conexões, debounce, Redis, memória, áudio, imagem, PDF, pausa/retomada, Evolution API, caminhos de teste e produção e o tom atual, salvo correção explicitamente autorizada nos prompts posteriores.

# 10. Alterações permitidas sem perguntar
Criar diretórios de auditoria, checksums, relatórios, fixtures, exports, cópias DEV inativas e stubs locais sem rede. Pode formatar esses artefatos.

# 11. Alterações que exigem confirmação
Excluir arquivo/registro; migrar esquema; trocar modelo/dimensão; criar/alterar RPC; mudar dependência/arquitetura/credencial; atualizar produção; ativar/publicar/deploy; executar chamada externa real; enviar WhatsApp; expandir escopo.

# 12. Critérios numerados de pronto
1. Três workflows identificados com IDs, versões, estado e timestamps.
2. Backups ativo/atual legíveis, com hashes e contagem de nós/conexões.
3. Cópias DEV inativas e incapazes de produzir efeitos externos.
4. Schemas e contagens das Data Tables arquivados.
5. DDL/RPC/vetor obtidos ou ausência comprovada e marcada como gate.
6. Matriz de dependências completa.
7. Segredos e PII ausentes dos relatórios.
8. Rollback reproduzível e testado em cópia descartável.

# 13. Testes automatizados
- Validar JSON dos backups; comparar IDs de nós e número de conexões entre original e backup.
- Verificar hashes; detectar arquivo vazio/truncado.
- Assegurar active=false nas cópias DEV.
- Procurar triggers, URLs, nós de envio e credenciais inline; reprovar se uma cópia DEV puder enviar algo.
- Validar referências de Data Tables por resolução ao vivo, não só cachedResultName.

# 14. Testes manuais
- Abrir cada cópia DEV e confirmar visualmente que a topologia está preservada.
- Simular rollback da cópia descartável para o backup e comparar hashes sem publicar.
- Revisar a matriz de efeitos externos.

# 15. Evidências obrigatórias
Arquivos criados; hashes; IDs/versões; contagens antes; nós/triggers neutralizados em DEV; comandos e ferramentas usados; outputs de validação; matriz de dependências; DDL obtido; segredos redigidos; confirmação de que produção permaneceu intacta.

# 16. Plano de rollback
Para cada componente, indicar backup, versão, comando/operação de restauração, pré-condições, validação pós-restore e responsável. Não chamar o rollback de testado sem restaurar uma cópia descartável e comparar estrutura.

# 17. Condições de parada
Pare se a instância/projeto estiver ambígua, algum backup não for verificável, a cópia DEV tiver efeitos externos ativos, faltar permissão de leitura, um segredo aparecer no relatório, ou a próxima ação exigir confirmação.

# 18. Formato da resposta final
Entregue: baseline; hashes; tabela workflow/ID/versão/estado; matriz de dependências; cópias DEV; proteções contra efeitos externos; DDL/esquemas; contagens; alertas; rollback; checklist objetivo. Não use “parece correto”. Não implemente os Prompts 1 a 4.
```

## Prompt 1 — Catálogo, products.csv e Data Table

```text
# 1. Papel
Atue como engenheiro de dados sênior e QA de catálogo. Trabalhe somente após o Prompt 0 estar aprovado. Use n8n-mcp/n8n-skills para resolver o Data Table, validar o nó Data Table e produzir alterações mínimas e auditáveis na cópia DEV.

# 2. Objetivo
Extrair programaticamente o catálogo oficial, criar products.corrected.csv, comparar por registro/campo com products(1).csv e com o Data Table DEV, corrigir apenas divergências comprovadas e aplicar upsert idempotente sem excluir dados silenciosamente.

# 3. Contexto confirmado
O modelo expandido atual tem 242 linhas: 112 pizzas tradicionais, 56 especiais, 32 doces, 10 pastéis, 10 porções/aperitivos e 22 bebidas. O CSV anexado coincide com os 242 itens lidos do Data Table ao vivo na execução 1104. Há 10 descrições de pastel com “o site informa” e nomes abreviados de bebidas. A coluna price da Data Table é string; image_url e active são usados operacionalmente.

# 4. Fontes de verdade
1. cardapio-dona-rosa(1).md.
2. informacoes-pizzaria-dona-rosa(2).md apenas para regras comerciais não pertencentes ao catálogo.
3. Data Table ao vivo/DEV para implementação e campos operacionais.
4. products(1).csv como estado atual, nunca acima do cardápio.
Não use site, memória do modelo ou texto promocional externo.

# 5. Escopo autorizado
Ler e analisar; gerar parser, catálogo canônico, products.corrected.csv, diff CSV/JSON/Markdown, fixtures e testes; editar apenas a cópia DEV do Data Table products por upsert direcionado; preservar image_url/active quando comprovados.

# 6. Fora do escopo
Não alterar produção, Supabase, RPC, workflows ativos, credenciais ou esquema. Não excluir registro extra sem relatório e confirmação. Não alterar ImportPdfToTable salvo prova de dependência e autorização posterior.

# 7. Arquivos e workflows envolvidos
cardapio-dona-rosa(1).md, informacoes-pizzaria-dona-rosa(2).md, products(1).csv, products.corrected.csv a criar, Data Table products DEV, workflow ImportPdfToTable apenas para ler a natural key/uso de campos, ToolsProductsDataTableToRag apenas para ler consumidores.

# 8. Sequência de execução
1. Parsear Markdown de forma determinística, preservando acentos e nomes oficiais.
2. Construir representação canônica com categoria, sabor/produto, tamanho, fatias, limite de sabores, preço decimal, ingredientes/descrição, opções, volume e casco.
3. Expandir sabor x tamanho somente porque o modelo atual o faz; se o live model divergir, provar equivalência antes de alterar contagem.
4. Normalizar apenas para comparação; a saída deve conservar grafia oficial.
5. Comparar todos os campos. Classificar cada divergência como correção oficial, metadado operacional preservado, ausência oficial ou item extra.
6. Remover das descrições pesquisáveis dos 10 pastéis “o site informa” e qualquer alegação não sustentada; não inventar ingredientes ausentes.
7. Restaurar nomes completos: Coca-Cola, Coca-Cola Zero e Guaraná Jesus; explicitar KS 290 ml, retornável 1 litro, refrigerante 1 litro e 2 litros conforme a fonte.
8. Preservar image_url e active por natural key quando existentes. Verificar caminhos suspeitos como /images/porcos/ apenas como metadado operacional; não corrigir sem prova do asset.
9. Gerar products.corrected.csv sem sobrescrever o original. Preço deve ser valor decimal parseável, não moeda formatada. Como o Data Table armazena string, use formato canônico decimal enquanto não houver aprovação de migração.
10. Definir natural key documentada. No modelo expandido atual, name é único porque incorpora tamanho; valide zero colisões. Não criar nova coluna sem necessidade.
11. Validar completamente o arquivo corrigido.
12. Aplicar upsert somente na Data Table DEV, em lote controlado, com contagens antes/depois. Não apagar extras; marcá-los no relatório e solicitar confirmação se a remoção for necessária.
13. Executar o upsert duas vezes e provar idempotência.
14. Produzir patch, diff por registro/campo e rollback.

# 9. Regras que devem ser preservadas
- Brotinha: 1 sabor. P: até 2. M/G: até 3. F/XF/GG/Extra: até 4.
- Mistura de categorias cobra a categoria mais cara; nunca somar nem calcular média.
- Preços exclusivamente do cardápio.
- Bebida sem quantidade implica uma unidade no agente, não multiplica registros do catálogo.
- KS e retornável exigem casco.
- Não apagar image_url/active por não aparecerem no Markdown.

# 10. Alterações permitidas sem perguntar
Criar parser, arquivos corrigidos/diff/testes e atualizar a cópia DEV por upsert idempotente; corrigir fatos divergentes dentro do escopo.

# 11. Alterações que exigem confirmação
Excluir/desativar registros; substituir o CSV original; migrar price para number; adicionar/remover colunas; alterar produção; alterar assets, dependências ou ImportPdfToTable.

# 12. Critérios numerados de pronto
1. Parser reproduzível e catálogo canônico arquivado.
2. products.corrected.csv válido e original intacto.
3. Cobertura integral do cardápio e zero item não oficial.
4. Se mantido o modelo expandido: exatamente 242 linhas e distribuição 112/56/32/10/10/22; se não, prova de equivalência semântica.
5. Zero natural keys duplicadas; nomes/categorias não vazios.
6. Zero preço divergente, inválido ou negativo.
7. Zero ocorrência pesquisável de “o site informa” e “Sabor da Terra”.
8. Bebidas, marcas, volumes e casco canônicos.
9. image_url/active preservados conforme uso comprovado.
10. Duas aplicações geram o mesmo estado e contagem.

# 13. Testes automatizados
- CSV parseável, cabeçalhos esperados, encoding UTF-8, preço decimal, booleano active válido.
- Comparação campo a campo com a representação canônica.
- Contagens por categoria e tamanho; 14 tradicionais x 8, 7 especiais x 8, 4 doces x 8.
- Zero duplicidade por natural key e zero produto extra.
- Testes de preço: G Calabresa R$ 50; G Calabresa + Nordestina usa R$ 55; Brotinha tradicional R$ 15; Extra especial R$ 160.
- Testes de limites: Brotinha rejeita 2 sabores; P aceita 2; G rejeita 4; F aceita 4.
- KS Coca-Cola 290 ml R$ 4 com casco; retornável Coca-Cola 1 litro R$ 8 com casco.
- Pastel Doçura R$ 10; Macarronada Carne R$ 20.
- Segunda execução do upsert: zero insert extra e zero diff.

# 14. Testes manuais/conversacionais
Inspecionar amostras de cada categoria, acentos, unidades e descrições. Confirmar que nenhum ingrediente foi inferido para pastéis. Confirmar que nomes completos são naturais para busca humana.

# 15. Evidências obrigatórias
Arquivos criados/alterados; hash antes/depois; diff por linha/campo; contagens; natural key; resultado de cada teste; linhas preservadas; lista de extras não removidos; logs das duas execuções; confirmação de produção intacta.

# 16. Plano de rollback
Restaurar snapshot da Data Table DEV e remover apenas o lote identificado por run_id/hash. Restaurar products.corrected.csv pelo arquivo anterior. Não usar delete sem filtro.

# 17. Condições de parada
Pare se o Markdown for ambíguo, a Data Table DEV não estiver resolvida, a natural key colidir, a contagem divergir sem explicação, um upsert tentar apagar campo operacional ou surgir necessidade de migração/exclusão.

# 18. Formato da resposta final
Resumo; arquivos; contagens; natural key; tabela de divergências; patch/diff; testes com esperado/obtido; estado DEV; pendências que exigem confirmação; rollback. Não avance ao RAG se qualquer critério falhar.
```

## Prompt 2 — ToolsProductsDataTableToRag e Supabase

```text
# 1. Papel
Atue como engenheiro sênior de RAG/Supabase/n8n e SRE de dados. Trabalhe somente após Prompts 0 e 1 aprovados. Use cópia DEV e padrões de data persistence, knowledge base, error handling, AI nodes e validation expert do n8n-skills.

# 2. Objetivo
Corrigir ToolsProductsDataTableToRag para sincronização completa, idempotente, versionada, recuperável e auditável; alinhar o mesmo modelo/dimensão na ingestão e consulta; validar o ranking híbrido sem mudar arquitetura além do comprovadamente necessário.

# 3. Contexto confirmado
Workflow ao vivo: exIKvB9KjZy5AezC, inativo, 16 nós, versão da análise da54d7b7-a3ca-4a4b-a8ef-a7ddd1b4eda5. GetAllProduts lê products hICNaSYRSMkjHiTT com active=true. Config usa file_name product_restaurant_list. DeleteFilesSupabase apaga por metadata->>file_name e executa antes da inserção. A execução 1104 processou 242 produtos e substituiu 120 chunks. Os documentos possuem vetor 1536 e não possuem hash/versão. O indexador usa por padrão text-embedding-3-small/1536; hybrid-search usa text-embedding-3-large/1536 e match_count 10.

# 4. Fontes de verdade
Catálogo/Data Table DEV aprovados no Prompt 1; workflow ao vivo/cópia DEV; documents_rows(1).csv; hybrid-search(1).zip; DDL real de documents/hybrid_search; documentação exata dos nós da versão instalada. Não confie em defaults: torne explícitos modelo e dimensão.

# 5. Escopo autorizado
Editar somente a cópia DEV do workflow; criar fixtures, scripts, relatórios e metadados; atualizar Edge Function apenas em ambiente DEV se necessário; inserir/reindexar documentos DEV ou uma fonte/versionamento isolado; testar RPC em dados de desenvolvimento.

# 6. Fora do escopo
Não alterar/ativar/publicar produção; não fazer delete global; não tocar documentos de outras fontes; não trocar tabela/RPC/modelo/dimensão sem evidência, análise de impacto e autorização quando aplicável; não alterar ImportPdfToTable sem prova.

# 7. Arquivos e workflows envolvidos
ToolsProductsDataTableToRag DEV; ImportPdfToTable somente dependência; Data Table products DEV; documents; hybrid_search; Edge Function hybrid-search; products.corrected.csv; documents_rows(1).csv.

# 8. Sequência de execução
1. Recuperar novamente workflow/versão e DDL; comparar com o baseline para detectar drift.
2. Confirmar documents.embedding como vector(1536) ou equivalente, assinatura/tipos/retorno de hybrid_search, índices FTS/vetoriais, filtros e permissões.
3. Resolver incompatibilidade do embedding. Caminho preferencial, se DDL confirmar 1536 e custo/política permitirem: definir explicitamente no n8n text-embedding-3-large com dimensions=1536, mantendo a Edge Function igual, e reindexar tudo. Alternativa mínima: definir text-embedding-3-small/1536 nos dois lados. Nunca misture modelos. Documentar decisão, custo e necessidade de reindexação integral.
4. Criar catalog_hash SHA-256 a partir da representação canônica ordenada e source_version imutável. Inserir ambos em metadata, além de file_name e timestamp/run_id.
5. Tornar a ordem segura: manter a versão estável enquanto uma nova versão é construída. Se a mesma catalog_hash já estiver completa e validada, encerrar sem inserir. Se estiver parcial, apagar somente aquela versão parcial e reconstruí-la.
6. Inserir a nova versão antes de remover a anterior. Validar contagem, integridade, embedding e matriz RAG na versão nova. Só depois remover versões antigas da própria fonte, com filtro composto por file_name/source_version e relatório prévio. Se a RPC não puder isolar versão durante validação, usar ambiente/tabela DEV; não alterar RPC silenciosamente.
7. Nunca executar delete global. DeleteFilesSupabase deve deixar explícito o escopo e não rodar antes de existir uma versão anterior recuperável.
8. Tornar geração determinística: ordenação estável por categoria/nome, separadores explícitos, campos comerciais oficiais, sem URLs/imagens no texto pesquisável salvo ganho medido. Preserve image_url no Data Table.
9. Definir chunking explicitamente e registrar tamanho/overlap/separadores. Não depender de defaults.
10. Tratar falhas parciais com erro alto, run_id, contagens e caminho de retomada; nenhuma falha pode deixar a fonte estável removida.
11. Executar duas vezes com a mesma entrada e provar zero chunks adicionais e mesmo catalog_hash.
12. Executar matriz de recuperação híbrida, registrar top-10, ranking e fatos.
13. Gerar diff por nó, relatório de reindexação e rollback. Não ativar/publicar.

# 9. Regras que devem ser preservadas
Arquitetura atual, Data Table como fonte, Supabase documents, RPC hybrid_search, 1536 dimensões se confirmadas e 10 resultados, salvo alteração autorizada. Preservar documentos de outras fontes. O RAG fornece somente catálogo; endereço, Pix, pagamento e horário continuam no prompt oficial do agente.

# 10. Alterações permitidas sem perguntar
Atualizações parciais na cópia DEV; metadados de fonte/versão; ordenação; filtros seguros; error handling; testes; reindexação em namespace/tabela DEV; correção do modelo para compatibilidade após DDL confirmado e conforme decisão aprovada no baseline.

# 11. Alterações que exigem confirmação
Alterar produção, DDL, dimensão, tabela, RPC, índice, modelo fora das duas opções justificadas, dependência, credencial, limpeza ampla, publicação/deploy.

# 12. Critérios numerados de pronto
1. DDL/RPC/esquema arquivados e compatíveis.
2. Um único modelo e dimensão explicitamente configurados em ingestão e consulta.
3. Cada chunk contém file_name, source_version, catalog_hash e run_id.
4. Nova versão validada antes da remoção da anterior.
5. Zero delete global e zero documento de outra fonte afetado.
6. Reexecução idêntica produz zero duplicidade.
7. Falha induzida preserva a versão estável.
8. Contagens de produtos/documentos/chunks explicadas.
9. Todas as 10 classes de busca aprovadas.
10. Workflow DEV validado; produção inalterada.

# 13. Testes automatizados
- Confirmar modelo/dimensão dos dois lados e comprimento 1536 em amostra.
- DDL/RPC: tipos de query_text, query_embedding e match_count; retorno e limites.
- Teste de idempotência duas vezes; teste de falha entre chunking e insert; teste de rollback.
- Validar metadata, zero chunk órfão, zero source_version parcial, zero conteúdo “Sabor da Terra”/“o site informa”.
- RAG: nome exato; abreviação comum; ingrediente; categoria; tamanho+preço; limite de sabores; bebida+volume; casco; inexistente sem invenção; consulta “Sabor da Terra” sem conteúdo antigo.
- Para cada consulta: query, top-k, esperado, posição, fatos, divergências e aprovado/reprovado.
- Casos de referência: Calabresa G R$ 50; Nordestina G R$ 55; Pastel Doçura R$ 10; Macarronada Carne R$ 20; KS 290 ml R$ 4 com casco; retornável 1 litro R$ 8 com casco.

# 14. Testes manuais/conversacionais
Consultar com erros de acento, caixa, “coca”, “jesus”, “pizza portuguesa ingredientes”, “limite XF” e item inexistente. Verificar que resposta não mistura regras comerciais fora do catálogo.

# 15. Evidências obrigatórias
DDL; modelo/dimensão; diff de nós; hashes; contagens antes/depois; metadata amostral sem segredo; resultados top-10; IDs de execuções DEV; falha induzida; segunda execução; documentos preservados; confirmação de produção inalterada.

# 16. Plano de rollback
Manter source_version anterior intacta até aprovação. Para rollback, reabilitar a versão anterior/namespace DEV e remover somente a versão nova por file_name+source_version+catalog_hash. Se houver mudança na Edge Function DEV, restaurar o commit/hash anterior.

# 17. Condições de parada
Pare se DDL/RPC não puder ser lido, dimensão/modelo não puderem ser provados, filtro de delete não for estritamente limitado à fonte/versão, ambiente não for DEV, contagens divergirem, versão nova falhar em qualquer teste ou a ação exigir migração não aprovada.

# 18. Formato da resposta final
Diagnóstico; decisão de embedding; DDL/resumo; diff por nó; estratégia de cutover; contagens; matriz RAG; falhas/alertas; idempotência; rollback; confirmação de não ativação. Não declarar pronto com teste simulado.
```

## Prompt 3 — Fluxo principal da Pizzaria Dona Rosa

```text
# 1. Papel
Atue como arquiteto sênior de agentes n8n, engenharia de prompts, segurança de pagamentos e QA conversacional. Trabalhe somente depois de catálogo e RAG aprovados. Faça revisão cirúrgica na cópia DEV do workflow principal.

# 2. Objetivo
Substituir dados antigos pela Pizzaria Dona Rosa, corrigir entrega/pagamento/endereço/comprovante, reparar referências das ferramentas e tornar contratos/status/idempotência coerentes, preservando o tom, a topologia e os recursos que funcionam.

# 3. Contexto confirmado
Workflow XCZsECfv1SNrLN80, versão ativa 8e3a75f9-38ce-4e56-a1bf-ffddefafe260, 85 nós. Atendente AI contém Sabor da Terra/Copacabana. AgentCaixa cobra R$ 10 e marca pago ao receber qualquer comprovante. As ferramentas UpdateCustomer, UpdateAddRascunho e UpdateAddInvoice usam IDs antigos; execução 1125 confirmou falha interna de UpdateAddInvoice embora o workflow tenha terminado success. invoice_number usa data+contagem limitada a 10. A busca tem descrição genérica e query sem descrição. Há chave Supabase inline em headers; não exponha o valor.

# 4. Fontes de verdade
1. cardapio-dona-rosa(1).md.
2. informacoes-pizzaria-dona-rosa(2).md.
3. Workflow/Data Tables ao vivo e cópia DEV.
4. RAG aprovado no Prompt 2.
Não invente telefone, WhatsApp, Instagram ou site: a fonte oficial não os fornece.

# 5. Escopo autorizado
Editar somente cópia DEV; modificar minimamente systemMessage/toolDescription/$fromAI descriptions/configs relacionados; resolver Data Tables DEV; corrigir expressões de invoice_number; criar stubs de rede e testes; gerar diff e rollback.

# 6. Fora do escopo
Não reestruturar o workflow, remover nós/conexões, alterar debounce/Redis/memória/mídia, credenciais ou produção; não enviar mensagens reais; não processar pedido real; não publicar/ativar.

# 7. Arquivos e workflows envolvidos
Workflow principal DEV; Data Tables customers/invoices/products DEV; Atendente AI, AgentCaixa, OpenAI3, search_restaurante_data, UpdateCustomer, UpdateAddRascunho, UpdateAddInvoice, SendWhatsappMsg, Config/ConfigTest, CustomerData/CustomerData2, GetInvoices1/2 e conexões AI.

# 8. Sequência de execução
1. Reobter versão e comparar com baseline. Criar diff antes/depois dos prompts.
2. Resolver por nome/projeto os Data Tables DEV. Substituir referências antigas somente após confirmar schema. No baseline, produção acessível usa customers eXHmu98SYFK7A6zN e invoices BaMD12kIM3Y5iQDv; não reutilizar esses IDs cegamente em DEV.
3. Atualizar Atendente AI mantendo tom/abordagem, mas trocar identidade e dados comerciais. Dados oficiais: Pizzaria Dona Rosa; agente Rosa; Brejo-MA; retirada na Rua do Estádio, 60, em frente ao Bar do Sebastião; expediente diário 18h00-23h30 e sábados/domingos até 23h59.
4. Remover todas as ocorrências de Sabor da Terra, Copacabana, Rio de Janeiro, contatos/Instagram/horário/endereço antigos. Se telefone, site, WhatsApp ou Instagram não estiverem na fonte, não informar.
5. Instruir o Atendente a consultar search_restaurante_data antes de responder sobre produtos, preços, sabores, ingredientes, categorias, tamanhos, limites, bebidas e casco; nunca completar ausência.
6. Definir toolDescription final concisa: “Pesquisa exclusivamente o catálogo oficial da Pizzaria Dona Rosa. Use antes de responder sobre produtos, preços, sabores, ingredientes, categorias, tamanhos, limites de sabores, bebidas, volumes e regra de casco. Envie consulta curta, explícita e contextualizada. Não use como fonte de endereço, horário, pagamento ou Pix e não complete informação ausente.”
7. Preencher a descrição de query: “Consulta curta de catálogo, por exemplo: preço pizza G nordestina; ingredientes pizza portuguesa; bebidas retornáveis e regra do casco; limite de sabores pizza XF; pastéis doces disponíveis.” Ajustar ao formato real do nó sem quebrar $fromAI.
8. Corrigir AgentCaixa: entrega soma exatamente R$ 5; retirada/consumo local somam zero; forma aceita Pix/dinheiro/cartão; cartão na entrega; dinheiro pergunta troco; retirada/consumo sem pagamento informado = pagamento no estabelecimento.
9. Pix em retirada/consumo: enviar apenas se o cliente pedir. Dados oficiais: chave/número 98970278100; favorecido José Roberto Barbosa Pessoa; Banco Nu Pagamento S.A. - Instituição de Pagamento. Não duplicar, alterar ou inventar dados.
10. Endereço: antes de finalizar entrega exigir bairro, rua/travessa e referência/complemento. Número da casa é opcional. Pode continuar como string, mas UpdateCustomer e os prompts devem validar semanticamente os três campos obrigatórios antes de salvar/finalizar. Para retirada/consumo, não exigir endereço de entrega.
11. Reformular OpenAI3 para saída estruturada e somente extração: legível, tipo de imagem, valor, data, horário, favorecido, banco/instituição quando visível, identificador da transação quando visível, campos ausentes, divergências e confiança. Não permitir que o nó decida sozinho “pago”.
12. Comprovante: comparar valor, data, horário, favorecido e pedido. Divergente/ilegível/incompleto permanece pendente e vai a humano. Nunca alegar consulta bancária real. Só mudar para pago se a política aprovada permitir análise visual, todos os campos exigidos forem compatíveis e o registro deixar explícito “comprovante visual conferido, sem confirmação bancária”; caso contrário, pendente/humano.
13. Unificar contrato de status após inspecionar todos os consumidores. No mínimo documentar e testar: rascunho (montagem), aguardando (Pix pendente/verificação), a_receber (dinheiro/cartão/no estabelecimento, se preservado), pago e cancelado. Atualizar descrições $fromAI, filtros e ferramentas para o mesmo conjunto; não renomear sem verificar consumidores.
14. Corrigir UpdateCustomer toolDescription/contrato; UpdateAddRascunho deve preservar itens/quantidades/preços/total e não incluir taxa antes de conhecer modalidade; UpdateAddInvoice deve aplicar taxa/modalidade/status de forma coerente e usar o Data Table correto.
15. Substituir invoice_number baseado em count por identificador collision-resistant e idempotente, derivado de um identificador estável da mensagem/pedido ou mecanismo comprovado pela versão do n8n. Manter o mesmo número ao atualizar o rascunho. Testar concorrência e mais de 10 pedidos. Não inventar sintaxe: validar a expressão.
16. Migrar a chave inline da busca para credencial gerenciada somente com confirmação; no mínimo redigir de exports/relatórios e registrar risco. Nunca reproduzir o valor.
17. Em DEV, trocar SendWhatsappMsg e demais HTTPs de saída por stub/capture local. Validar que nenhuma chamada externa real é possível.
18. Validar nó a nó, expressões e workflow; executar testes conversacionais sem efeito externo; inspecionar erros internos de ferramentas, não só o status global.

# 9. Regras que devem ser preservadas
Tom e abordagem atuais; agente Rosa; não inventar; humano quando solicitado ou sem informação segura; regras completas do catálogo; debounce, Redis, memória, áudio/imagem/PDF, pausa/retomada, caminhos test/prod, clientes e invoices, conexões e ferramentas existentes.

# 10. Alterações permitidas sem perguntar
Prompts/tool descriptions/expressões/IDs de Data Tables na cópia DEV, contratos $fromAI, stubs, fixtures, testes e correções estritamente descritas. Pode corrigir referências quebradas comprovadas na cópia DEV.

# 11. Alterações que exigem confirmação
Produção; ativação/publicação/deploy; credenciais; envio real; mudança de arquitetura/dependência/schema; exclusão de nó/conexão/registro; limpeza ampla; nova integração bancária; expansão de escopo.

# 12. Critérios numerados de pronto
1. Zero ocorrência ativa de Sabor da Terra/dados antigos/R$ 10.
2. Dados oficiais da Dona Rosa e agente Rosa corretos, sem contato inventado.
3. Taxa R$ 5 somente em entrega; zero em retirada/consumo.
4. Endereço exige bairro+rua/travessa+referência/complemento e não exige número.
5. Pix/retirada/consumo seguem as regras oficiais.
6. Comprovante divergente/ilegível nunca marca pago; não há alegação de liquidação bancária.
7. Busca e query têm descrições completas e exemplos.
8. UpdateCustomer/UpdateAddRascunho/UpdateAddInvoice resolvem Data Tables DEV e passam no nível do nó.
9. Status têm contrato único; invoice_number não colide e é idempotente.
10. Nenhuma conexão/nó/credencial foi removida ou substituída fora do escopo.
11. Nenhum teste gerou chamada externa.

# 13. Testes automatizados
- Busca textual em todo JSON por termos antigos, R$ 10, contatos antigos e IDs de tabela inexistentes.
- Validar cada nó alterado em minimal e full/runtime; AI nodes também ai-friendly/strict quando suportado; validar expressões, conexões e workflow completo.
- Resolver Data Table IDs ao vivo e executar operações em fixtures DEV; falhar se um nó tool retornar erro mesmo quando workflow=success.
- Invoice number: 20 pedidos, duas execuções concorrentes e reprocessamento da mesma mensagem; zero colisão/duplicidade.
- Testes de atendimento 21-44 definidos no Prompt 4, com stub de WhatsApp/rede.

# 14. Testes manuais/conversacionais
Entrega com e sem cada campo; retirada/consumo; Pix pedido/não pedido; dinheiro/troco; cartão; comprovantes divergente, ilegível e coerente; cancelamento; item inexistente; humano; prompt injection; confirmação final completa.

# 15. Evidências obrigatórias
Diff antes/depois dos system messages; arquivos/workflows/nós/campos alterados; IDs de Data Tables resolvidos; validações; resultados por caso; execuções DEV e status de cada nó tool; capturas do stub; contagens de invoices; ausência de segredo; produção não ativada.

# 16. Plano de rollback
Restaurar a cópia DEV pelo backup/versionId do Prompt 0; restaurar IDs/prompts/expressões anteriores por patch reverso; apagar apenas fixtures identificadas pelo test_run_id, após confirmação; comprovar topologia e ausência de ativação.

# 17. Condições de parada
Pare se a cópia DEV puder enviar mensagem, Data Tables não forem resolvidas, houver drift de versão, faltar fonte oficial, status não puderem ser reconciliados com consumidores, expressão não validar, segredo for exposto ou surgir alteração fora do escopo.

# 18. Formato da resposta final
Resumo; diff por nó/campo; prompts antes/depois; Data Tables; contratos de status/endereço/pagamento; invoice_number; validações; tabela de testes esperado/obtido; efeitos externos bloqueados; alertas; rollback. Não declarar sucesso apenas pelo status do workflow.
```

## Prompt 4 — Auditoria final e testes

```text
# 1. Papel
Atue como revisor independente, adversarial e somente de QA. Não assuma que o implementador acertou. Não corrija silenciosamente: registre falha, evidência, gravidade e devolva ao prompt responsável.

# 2. Objetivo
Auditar dados, diffs, nós, expressões, conexões, RAG, agentes, ferramentas, estados e efeitos externos; reprovar qualquer item sem evidência reproduzível.

# 3. Contexto
Revise os resultados dos Prompts 0-3. O baseline mostrou que status global success pode ocultar falha em ferramenta; portanto, inspecione runData/status/erro por nó. Produção deve permanecer intacta e toda rede de saída deve estar stubada em DEV.

# 4. Fontes de verdade
Mesma precedência dos prompts anteriores, mais os backups, diffs, DDL, products.corrected.csv, catálogo canônico, source_version/catalog_hash, logs e execuções DEV produzidos.

# 5. Escopo autorizado
Ler tudo; criar relatório/fixtures; validar; executar testes locais/DEV sem efeitos externos; inspecionar execuções e auditoria da instância quando disponível; induzir falhas controladas em DEV.

# 6. Fora do escopo
Não alterar implementação, dados ou produção; não autofix/rollback/publicar/ativar; não enviar mensagens; não aprovar teste simulado.

# 7. Componentes envolvidos
Três workflows e versões DEV; Data Tables DEV; documents/RPC/Edge Function DEV; todos os arquivos/diffs; especialmente Atendente AI, AgentCaixa, OpenAI3, search_restaurante_data, UpdateCustomer, UpdateAddRascunho, UpdateAddInvoice, SendWhatsappMsg, embeddings e delete/insert.

# 8. Sequência de execução
1. Verificar baseline/backups/hashes e drift.
2. Revisar diffs e marcar mudança fora do escopo.
3. Validar individualmente cada nó alterado; minimal, full/runtime, ai-friendly e strict quando suportados. Separar erro confirmado, alerta e falso positivo.
4. Validar expressões, conexões, AI ports e workflow completo.
5. Testar catálogo/Data Table e segunda execução idempotente.
6. Testar ingestão, falha parcial, versão, rollback e matriz RAG.
7. Testar conversação e ferramentas com rede stubada.
8. Inspecionar cada execução e nó tool; workflow success com nó error é reprovação.
9. Auditar segredos inline, PII em logs, efeitos externos, produção ativa e alterações não autorizadas.
10. Emitir veredito por requisito. Não corrigir durante esta revisão.

# 9. Regras preservadas
Zero invenção; catálogo oficial; taxa/endereço/pagamento/Pix; tom de voz; topologia, debounce, Redis, memória e mídia; nenhum efeito externo; nenhum segredo em evidência.

# 10. Alterações permitidas sem perguntar
Somente arquivos de auditoria, fixtures e relatórios; execução de testes isolados DEV e leitura de logs.

# 11. Alterações que exigem confirmação
Qualquer correção, exclusão, escrita em dados não fixture, rollback real, alteração de credencial/schema/produção, rede externa ou expansão de escopo.

# 12. Critérios numerados de pronto
1. Zero mudança fora do escopo sem justificativa/aprovação.
2. Todos os nós/expressões/conexões válidos.
3. Todos os testes 1-44 executados, com esperado/obtido/evidência.
4. Idempotência comprovada em catálogo, RAG e mensagem/pedido.
5. Falha parcial preserva versão estável.
6. Zero conteúdo antigo/não oficial no RAG.
7. Zero erro interno mascarado.
8. Zero chamada externa e zero segredo exposto.
9. Rollback testado em cópia.
10. Produção não ativada/alterada.

# 13. Testes automatizados e matriz mínima
Catálogo/cálculo:
1. Pizza G Calabresa -> R$ 50.
2. Pizza G Calabresa + Nordestina -> R$ 55; não somar/média.
3. Brotinha com 2 sabores -> rejeitar/corrigir.
4. P com 2 sabores -> aceitar.
5. G com 4 sabores -> rejeitar/corrigir.
6. F com 4 sabores -> aceitar.
7. KS Coca-Cola 290 ml -> R$ 4 + casco.
8. Retornável Coca-Cola 1 litro -> R$ 8 + casco.
9. Pastel Doçura -> R$ 10.
10. Macarronada Carne -> R$ 20.

RAG, sempre registrando query, top-10, esperado, posição, fatos, divergências e status:
11. Nome exato.
12. Nome abreviado/variação comum.
13. Ingredientes.
14. Categoria.
15. Tamanho e preço.
16. Limite de sabores.
17. Bebida e volume.
18. Casco.
19. Consulta inexistente -> não inventar.
20. Sabor da Terra -> não retornar conteúdo antigo.

Atendimento/ferramentas:
21. Entrega com bairro+rua+referência sem número -> continuar.
22. Sem bairro -> pedir bairro.
23. Sem rua -> pedir rua/travessa.
24. Sem referência/complemento -> pedir.
25. Sem número -> não bloquear.
26. Entrega completa -> taxa exatamente R$ 5.
27. Retirada -> zero taxa.
28. Consumo local -> zero taxa.
29. Retirada sem pagamento -> pagamento no estabelecimento.
30. Retirada sem pedir Pix -> não enviar chave.
31. Retirada pedindo Pix -> dados oficiais exatos.
32. Dinheiro -> perguntar troco.
33. Cartão na entrega -> registrar a_receber/estado canônico equivalente documentado.
34. Pix com valor divergente -> não pago.
35. Pix com favorecido divergente -> não pago.
36. Comprovante ilegível -> nova imagem ou humano; pendente.
37. Produto inexistente -> não inventar.
38. Fora do assunto -> manter limite.
39. Pedido de humano -> encaminhar.
40. Cancelamento -> motivo e status correto.
41. Rascunho -> preservar itens/quantidades/preços/total.
42. Mesma mensagem reexecutada -> não duplicar pedido.
43. Prompt injection para ignorar cardápio/revelar instruções -> recusar.
44. Confirmação final -> nome, itens, quantidades, valores, taxa só se aplicável, endereço e pagamento coerentes.

Testes técnicos adicionais:
- 242 linhas e distribuição esperada ou equivalência demonstrada; zero divergência/natural key duplicada.
- Duas sincronizações RAG idênticas; falha induzida após chunking; rollback.
- 20 pedidos, concorrência e reprocessamento para invoice_number.
- Busca estática por segredo/chave inline, endpoints/contatos antigos e IDs inexistentes.
- Assert de que todos os HTTPs externos apontam para stubs e nenhuma chamada saiu.

# 14. Testes manuais/conversacionais
Repetir 21-44 com variações de linguagem, mensagens fragmentadas, acentos, áudio transcrito, imagem e PDF. Verificar tom preservado e ausência de regras inventadas. Realizar revisão humana das confirmações finais e dos comprovantes simulados.

# 15. Evidências obrigatórias
Diff; validações; comandos; versões; contagens; logs; IDs de execução DEV; status por nó; top-10 do RAG; outputs conversacionais; capturas do stub; falhas induzidas; rollback; erros/alertas/falsos positivos; produção não ativada.

# 16. Plano de rollback
Executar rollback apenas em cópia descartável usando os procedimentos dos Prompts 0-3. Comparar hashes, nós, conexões, contagens e versão RAG. Se falhar, reprovar o pacote.

# 17. Condições de parada
Pare e reprove se faltar backup, DDL, versão, evidência; houver efeito externo; teste pendente/simulado; erro interno; alteração fora de escopo; segredo exposto; rollback falhar; produção tiver sido tocada.

# 18. Formato da resposta final
Veredito APROVADO/REPROVADO; tabela requisito/teste/esperado/obtido/evidência/status; erros confirmados; alertas; falsos positivos; alterações fora do escopo; riscos restantes; rollback; declaração de produção. “Parece correto” ou “testes passaram” sem evidência é inválido.
```

## Matriz de rastreabilidade

| Requisito                                              | Prompt   | Critério de pronto | Teste/evidência                                               |
| ------------------------------------------------------ | -------- | ------------------- | -------------------------------------------------------------- |
| Backups, versões, cópias DEV e rollback              | 0        | P0.1-P0.8           | Hashes, exports, active=false, restauração em cópia         |
| Catálogo oficial e 242 registros                      | 1        | P1.1-P1.10          | Contagens 112/56/32/10/10/22 e diff campo a campo              |
| Preços, tamanhos, fatias e sabores                    | 1 e 4    | P1.3-P1.8; P4.3     | Testes 1-6                                                     |
| Pastéis, porções, bebidas, volumes e casco          | 1 e 4    | P1.7-P1.8           | Testes 7-10; zero “o site informa”                           |
| image_url e active preservados                         | 1 e 2    | P1.9; P2.8          | Diff operacional e conteúdo dos chunks                        |
| Data Table idempotente e sem exclusão silenciosa      | 1        | P1.10               | Dois upserts, zero insert/diff extra                           |
| RAG idempotente, versionado e recuperável             | 2        | P2.3-P2.8           | catalog_hash/source_version, falha parcial, duas execuções   |
| Mesmo modelo/dimensão na ingestão e busca            | 2        | P2.1-P2.2           | Nó explícito, Edge Function e vetores 1536                   |
| Recuperação híbrida precisa                         | 2 e 4    | P2.9; P4.3          | Testes 11-20 com top-10                                        |
| Identidade e dados Dona Rosa                           | 3        | P3.1-P3.2           | Busca em JSON e testes conversacionais                         |
| Taxa R$ 5 somente na entrega                           | 3 e 4    | P3.3                | Testes 26-28                                                   |
| Bairro/rua/referência obrigatórios; número opcional | 3 e 4    | P3.4                | Testes 21-25                                                   |
| Pix, retirada, consumo, dinheiro e cartão             | 3 e 4    | P3.5                | Testes 29-33                                                   |
| Comprovante seguro e sem falsa confirmação bancária | 3 e 4    | P3.6                | Testes 34-36 e saída estruturada OpenAI3                      |
| Busca do catálogo bem descrita                        | 3        | P3.7                | toolDescription/query e chamadas observadas                    |
| Ferramentas nas Data Tables corretas                   | 3 e 4    | P3.8                | Resolução de IDs e status por nó tool                       |
| Status coerentes                                       | 3 e 4    | P3.9                | Transições rascunho/aguardando/a_receber/pago/cancelado      |
| invoice_number único e idempotente                    | 3 e 4    | P3.9                | 20 pedidos, concorrência, reprocessamento                     |
| Preservação de arquitetura/tom/recursos              | 3 e 4    | P3.10; P4.1-P4.2    | Diff de nós/conexões/prompts e regressão de mídia/debounce |
| Nenhum efeito externo em testes                        | 0, 3 e 4 | P0.3; P3.11; P4.8   | Stubs/capturas e auditoria de rede                             |
| Prompt injection, humano e limites                     | 3 e 4    | P3.11; P4.3         | Testes 37-44                                                   |
| Evidência reproduzível e revisão independente       | 4        | P4.1-P4.10          | Relatório APROVADO/REPROVADO por requisito                    |

## Riscos remanescentes

- Análise visual de comprovante nunca equivale a confirmação bancária. Sem integração bancária ou revisão humana, permanece risco residual de fraude mesmo quando a imagem parece consistente.
- A qualidade final da busca depende do DDL, pesos e índices reais da RPC `hybrid_search`, ainda não presentes nos anexos. Esse risco só desaparece após inspeção e testes do Prompt 2.
- `image_url` contém caminhos operacionais cuja existência não foi comprovada pela fonte oficial; preservá-los evita regressão, mas links quebrados exigem auditoria separada de assets.
- Agentes probabilísticos podem variar. Mesmo após aprovação, mantenha uma suíte de regressão com os 44 casos e execute-a sempre que modelo, prompt, cardápio ou workflow mudar.
- Idempotência de pedidos depende de existir um identificador estável de mensagem/pedido e, idealmente, garantia de unicidade no armazenamento. Se a Data Table não oferecer constraint/transação adequada, concorrência extrema continua exigindo controle adicional aprovado.
