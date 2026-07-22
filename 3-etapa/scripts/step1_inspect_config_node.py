import json

snapshot_path = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\3-etapa\output\wf_main_dev_pre_edit_snapshot.json"
with open(snapshot_path, encoding="utf-8") as f:
    wf = json.load(f)

config_node = next(n for n in wf["nodes"] if n["name"] == "Config")
print(json.dumps(config_node.get("parameters", {}), indent=2, ensure_ascii=False))
