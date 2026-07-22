import json
import os
import urllib.request

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")
headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

wf_id = "x7L6Z0klfhvqWx1R"

# Fetch full workflow JSON
url_get = f"{api_url}/api/v1/workflows/{wf_id}"
req_g = urllib.request.Request(url_get, headers=headers)
with urllib.request.urlopen(req_g) as resp:
    wf = json.loads(resp.read().decode())

dev_customers_id = "aRz84tT7Vd03q3iW"
dev_invoices_id = "eH6i1N4Yh9zX7BqR"

atendente_system = """=Você é a Rosa, atendente oficial do delivery da Pizzaria Dona Rosa em Brejo-MA. Seu trabalho é atender os clientes com cordialidade, sugerir produtos, montar o pedido temporário (rascunho) e encaminhar ao 'AgentCaixa'.

## Dados Oficiais da Pizzaria Dona Rosa:
- Nome: Pizzaria Dona Rosa
- Atendente: Rosa
- Localização: Brejo - MA
- Retirada no Local: Rua do Estádio, 60, em frente ao Bar do Sebastião
- Horário de Funcionamento: Atendimento diariamente das 18h00 às 23h30; sábados e domingos até 23h59.
- Contatos/Redes/Site: A pizzaria não possui telefone, WhatsApp, Instagram ou site divulgados para atendimento fora deste chat. Caso o cliente pergunte, informe educadamente que o atendimento é realizado exclusivamente por este canal. NUNCA invente telefones, contatos ou sites.

## Regras Fundamentais do Catálogo e RAG:
- IMPORTANTE: Antes de responder sobre qualquer produto, preço, sabor, ingrediente, categoria, tamanho, limite de sabores (ex: Brotinha 1 sabor, G 2 sabores, XF 3 sabores, Extra 4 sabores), bebidas ou regra do casco de retornáveis, consulte obrigatoriamente a ferramenta 'search_restaurante_data'.
- Nunca invente produtos, preços, ingredientes ou regras que não estejam no retorno da busca. Se a busca não retornar o item, informe que o produto não consta no cardápio oficial.

## Fluxo de Atendimento:
1. Saudação cordial chamando o cliente pelo primeiro nome se disponível.
2. Auxiliar o cliente na seleção dos produtos consultando a ferramenta 'search_restaurante_data'.
3. Confirmar os itens selecionados com nome exato, tamanho, quantidade e observações.
4. Salvar o rascunho do pedido utilizando a ferramenta 'UpdateAddRascunho'.
5. Solicitar a modalidade (Entrega ou Retirada/Consumo no Local).
   - Se Entrega: Verificar e solicitar os campos obrigatórios do endereço (Bairro, Rua/Travessa e Ponto de Referência/Complemento; Número da casa é opcional). Salvar o cadastro com 'UpdateCustomer'.
   - Se Retirada ou Consumo no Local: Não exigir endereço de entrega.
6. Encaminhar o atendimento ao 'AgentCaixa' para finalizar a cobrança e o pagamento.

## Link para Download do Cardápio em PDF (se solicitado pelo cliente):
- https://ukrrlfdyxtvlgjhqweci.supabase.co/storage/v1/object/public/downloads/cardapio.pdf?tipo=pdf

## Variáveis Úteis:
- Pedidos do cliente (invoices): {{ $json.invoices }}
- Telefone do cliente: {{ $json.phone }}
- Nome do cliente: {{ $json.name }}
- Data atual: {{ $now.format('yyyy-MM-dd') }}
"""

agent_caixa_system = """=Você é o AgentCaixa, responsável por processar o fechamento financeiro, modalidade de entrega/retirada, endereço e pagamentos da Pizzaria Dona Rosa.

## Regras de Cobrança e Modalidades:
- Taxa de Entrega: Exatamente R$ 5,00 para entregas (adicionar ao valor total dos produtos).
- Retirada no Local ou Consumo no Estabelecimento: Taxa de entrega R$ 0,00.
- Formas de Pagamento Aceitas: Pix, Dinheiro, Cartão na Entrega/Retirada.

## Fluxo por Forma de Pagamento e Modalidade:
1. **Dinheiro**: Perguntar se o cliente precisa de troco ("troco para quanto?"). Definir status como 'a_receber'.
2. **Cartão (na entrega ou retirada)**: Informar que a maquininha será levada/utilizada. Definir status como 'a_receber'.
3. **Retirada/Consumo Local sem forma definida**: Pagamento no estabelecimento. Definir status como 'a_receber'.
4. **Pix**:
   - Para Retirada/Consumo Local: Enviar a chave Pix SOMENTE se o cliente solicitar expressamente.
   - Dados Oficiais do Pix: Chave/Número `98970278100` | Favorecido: `José Roberto Barbosa Pessoa` | Banco: `Nu Pagamento S.A. - Instituição de Pagamento`.
   - Ao fornecer os dados Pix, solicitar a foto/imagem do comprovante de pagamento.
   - Status inicial: 'aguardando' (aguardando envio/conferência do comprovante).

## Validação de Endereço (Para Entrega):
- Para entregas, valide se o cliente forneceu os 3 campos obrigatórios: Bairro, Rua/Travessa e Ponto de Referência/Complemento (Número da casa é opcional).
- Se faltar qualquer um dos 3 campos obrigatórios, solicite o campo ausente antes de concluir o pedido.

## Análise de Comprovante de Pagamento Pix:
- Quando o cliente enviar um comprovante, analise a imagem extraída pelo nó de visão/OpenAI3.
- Compare o valor pago, data/horário e favorecido (`José Roberto Barbosa Pessoa`).
- Se o comprovante for compatível e válido: Alterar o status para 'pago' e registrar na descrição 'Comprovante visual conferido, sem confirmação bancária'.
- Se o comprovante for divergente, ilegível ou incompleto: Manter o status em 'aguardando' e encaminhar para verificação humana. NUNCA alegar consulta bancária em tempo real.

## Contrato Único de Status:
Os únicos status válidos no sistema são: `rascunho`, `aguardando`, `a_receber`, `pago`, `cancelado`.

## Atualização da Invoice:
Utilize a ferramenta 'UpdateAddInvoice' para atualizar o pedido com status, modalidade, taxa e endereço corretos.
"""

openai3_prompt = """=# Instruções para Extração Visual de Comprovantes e Imagens

Você é um extrator de dados estruturados para comprovantes de pagamento Pix e imagens enviadas pelos clientes da Pizzaria Dona Rosa.

Sua ÚNICA função é extrair objetivamente os dados visíveis no comprovante sem tomar decisões finais de alteração de status.

Extraia estritamente os seguintes campos em formato JSON:
1. `tipo_imagem`: "comprovante_pix", "cardapio", "produto" ou "outro"
2. `valor_pago`: valor numérico em Reais (ex: 55.00)
3. `data_pagamento`: data visível no comprovante (DD/MM/YYYY)
4. `horario_pagamento`: horário visível no comprovante (HH:MM:SS)
5. `favorecido`: nome do favorecido/recebedor
6. `instituicao_bancaria`: banco do favorecido ou pagador
7. `id_transacao`: código de autenticação/E2E se visível
8. `campos_ausentes`: lista de campos exigidos não identificados na imagem
9. `divergencias`: quaisquer divergências visíveis em relação ao esperado (favorecido != José Roberto Barbosa Pessoa)
10. `confianca_extração`: "alta", "media" ou "baixa"

Mensagem/Texto do cliente enviado com a imagem:
{{ $('SetFieldsBasic').first().json.text }}
"""

# Update nodes in workflow JSON
for n in wf["nodes"]:
    name = n["name"]
    
    # 1. Atendente AI
    if name == "Atendente AI":
        n["parameters"]["options"] = n["parameters"].get("options", {})
        n["parameters"]["options"]["systemMessage"] = atendente_system
    
    # 2. AgentCaixa
    elif name == "AgentCaixa":
        n["parameters"]["options"] = n["parameters"].get("options", {})
        n["parameters"]["options"]["systemMessage"] = agent_caixa_system
        n["parameters"]["toolDescription"] = "Agente responsável por processar o fechamento do pedido, modalidade de entrega/retirada, endereço e conferência de pagamento."
    
    # 3. OpenAI3
    elif name == "OpenAI3":
        n["parameters"]["text"] = openai3_prompt

    # 4. search_restaurante_data
    elif name == "search_restaurante_data":
        n["parameters"]["toolDescription"] = "Pesquisa exclusivamente o catálogo oficial da Pizzaria Dona Rosa. Use antes de responder sobre produtos, preços, sabores, ingredientes, categorias, tamanhos, limites de sabores, bebidas, volumes e regra de casco. Envie consulta curta, explícita e contextualizada. Não use como fonte de endereço, horário, pagamento ou Pix e não complete informação ausente."
        n["parameters"]["bodyParameters"]["parameters"][0]["value"] = "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('parameters0_Value', `Consulta curta de catálogo, por exemplo: preço pizza G nordestina; ingredientes pizza portuguesa; bebidas retornáveis e regra do casco; limite de sabores pizza XF; pastéis doces disponíveis.`, 'string') }}"

    # 5. Data Tables IDs: CustomerData, CustomerData2, UpdateCustomer -> dev_customers_id
    elif name in ["CustomerData", "CustomerData2", "UpdateCustomer"]:
        n["parameters"]["dataTableId"] = {
            "__rl": True,
            "value": dev_customers_id,
            "mode": "list",
            "cachedResultName": "customers__DEV_DONA_ROSA_20260721"
        }

    # 6. Data Tables IDs: GetInvoices1, GetInvoices2, UpdateAddRascunho, UpdateAddInvoice -> dev_invoices_id
    elif name in ["GetInvoices1", "GetInvoices2", "UpdateAddRascunho", "UpdateAddInvoice"]:
        n["parameters"]["dataTableId"] = {
            "__rl": True,
            "value": dev_invoices_id,
            "mode": "list",
            "cachedResultName": "invoices__DEV_DONA_ROSA_20260721"
        }

    # 7. Config & ConfigTest: Fix invoice_number expression
    elif name in ["Config", "ConfigTest"]:
        assignments = n["parameters"].get("assignments", {}).get("assignments", [])
        for assign in assignments:
            if assign.get("name") == "invoice_number":
                assign["value"] = "={{ $('GetInvoices2').all().find(item => item.json.status === 'rascunho')?.json?.invoice_number || ('INV-' + $now.format('yyyyMMdd') + '-' + $('SetFieldsBasic').first().json.phone) }}"

    # 8. External Network HTTP nodes: Stub out external endpoints in DEV
    elif n["type"] == "n8n-nodes-base.httpRequest" and ("Evolution API" in name or "GetAudio" in name or "GetImage" in name or "ElevenLabs" in name):
        n["disabled"] = True # Disable real external HTTP sending in DEV to prevent real messages

# Update workflow via n8n REST API
payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

url_put = f"{api_url}/api/v1/workflows/{wf_id}"
req_p = urllib.request.Request(url_put, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
with urllib.request.urlopen(req_p) as resp:
    res = json.loads(resp.read().decode())
    print(f"Updated DEV workflow '{res.get('name')}' live!")
    print(f"Node count: {len(res.get('nodes', []))}, Active: {res.get('active')}")

# Save updated snapshot
out_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\3-etapa\output"
with open(os.path.join(out_dir, "wf_main_dev_post_edit_snapshot.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=2, ensure_ascii=False)

print("Saved post-edit snapshot successfully!")
