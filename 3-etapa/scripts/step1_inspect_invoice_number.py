import json

snapshot_path = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\3-etapa\output\wf_main_dev_pre_edit_snapshot.json"
with open(snapshot_path, encoding="utf-8") as f:
    wf = json.load(f)

nodes_by_name = {n["name"]: n for n in wf["nodes"]}

targets = ["Config", "ConfigTest", "SetFieldsBasic", "Merge1", "DivideEm3Blcos"]

for name in targets:
    if name in nodes_by_name:
        n = nodes_by_name[name]
        print(f"\n=================== {name} ({n['id']}) ===================")
        print(json.dumps(n.get("parameters", {}), indent=2, ensure_ascii=False))
