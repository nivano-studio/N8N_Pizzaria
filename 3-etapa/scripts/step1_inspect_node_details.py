import json
import os

snapshot_path = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\3-etapa\output\wf_main_dev_pre_edit_snapshot.json"
with open(snapshot_path, encoding="utf-8") as f:
    wf = json.load(f)

nodes_by_name = {n["name"]: n for n in wf["nodes"]}

targets = [
    "Atendente AI", "AgentCaixa", "OpenAI3", "search_restaurante_data",
    "UpdateCustomer", "UpdateAddRascunho", "UpdateAddInvoice",
    "CustomerData", "CustomerData2", "GetInvoices1", "GetInvoices2"
]

for name in targets:
    if name in nodes_by_name:
        n = nodes_by_name[name]
        print(f"\n=================== {name} ({n['id']}) ===================")
        print("Type:", n["type"], "TypeVersion:", n.get("typeVersion"))
        print("Parameters:")
        print(json.dumps(n.get("parameters", {}), indent=2, ensure_ascii=False)[:1000])
