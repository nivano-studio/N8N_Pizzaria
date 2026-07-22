import json

snapshot_path = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\3-etapa\output\wf_main_dev_pre_edit_snapshot.json"
with open(snapshot_path, encoding="utf-8") as f:
    wf = json.load(f)

nodes_by_name = {n["name"]: n for n in wf["nodes"]}

atendente = nodes_by_name.get("Atendente AI", {})
caixa = nodes_by_name.get("AgentCaixa", {})
openai3 = nodes_by_name.get("OpenAI3", {})

print("=== ATENDENTE AI SYSTEM PROMPT ===")
print(atendente.get("parameters", {}).get("options", {}).get("systemMessage", "NOT FOUND"))

print("\n=== AGENT CAIXA SYSTEM PROMPT ===")
print(caixa.get("parameters", {}).get("options", {}).get("systemMessage", "NOT FOUND"))
print("\n=== AGENT CAIXA TOOL DESCRIPTION ===")
print(caixa.get("parameters", {}).get("toolDescription", "NOT FOUND"))

print("\n=== OPENAI3 TEXT / PROMPT ===")
print(openai3.get("parameters", {}).get("text", "NOT FOUND"))
