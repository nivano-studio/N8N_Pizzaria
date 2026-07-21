import json
import urllib.request
import urllib.error

edge_url = "https://qucikffpvnvzaxfyugwi.supabase.co/functions/v1/hybrid-search"

payload = {
    "query": "CALABRESA G"
}

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

req = urllib.request.Request(edge_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print("Edge Function hybrid-search status: SUCCESS")
        print(f"Total documents returned: {res.get('total')}")
        if res.get("documents"):
            print("Top result sample:", res["documents"][0].get("content")[:200])
except urllib.error.HTTPError as e:
    print(f"Edge Function error: {e.code} {e.reason}: {e.read().decode()}")
except Exception as e:
    print(f"Edge Function error: {e}")
