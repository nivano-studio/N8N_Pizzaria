import json

snapshot_path = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\3-etapa\output\wf_main_dev_pre_edit_snapshot.json"
with open(snapshot_path, encoding="utf-8") as f:
    wf = json.load(f)

for n in wf["nodes"]:
    node_str = json.dumps(n, ensure_ascii=False)
    if "invoice_number" in node_str:
        print(f"Node [{n['name']}] ({n['id']}) references 'invoice_number'")
