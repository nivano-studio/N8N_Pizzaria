import json
import urllib.request
import urllib.error

# Test calling hybrid_search RPC on Supabase PostgREST endpoint
rpc_url = "https://qucikffpvnvzaxfyugwi.supabase.co/rest/v1/rpc/hybrid_search"

# Payload for hybrid_search RPC: query_text, query_embedding (null/empty array or 1536 float list), match_count
payload = {
    "query_text": "Calabresa G",
    "query_embedding": [0.0] * 1536,
    "match_count": 10
}

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

req = urllib.request.Request(rpc_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print(f"RPC hybrid_search SUCCESS -> Returned {len(res)} documents")
        if res:
            print("Sample doc 0 keys:", list(res[0].keys()))
            print("Sample doc 0 metadata:", res[0].get("metadata"))
except urllib.error.HTTPError as e:
    print(f"RPC hybrid_search FAILED -> {e.code} {e.reason}: {e.read().decode()[:200]}")
except Exception as e:
    print(f"RPC hybrid_search error: {e}")
