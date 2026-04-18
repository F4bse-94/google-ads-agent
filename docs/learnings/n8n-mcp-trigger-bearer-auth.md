---
name: n8n MCP Trigger Bearer-Auth automatisieren
description: Wie man fuer alle MCP-Trigger in einem Rutsch Bearer-Auth aktiviert — Credential-Create via Public API + update_partial_workflow via MCP
type: reference
---

# n8n MCP Trigger Bearer-Auth automatisieren

**Problem:** Die `@n8n/n8n-nodes-langchain.mcpTrigger` Nodes haben standardmaessig `authentication: "none"` — die Endpoints sind oeffentlich erreichbar. Fuer Production-Use (insbesondere bei Google-Ads-Write-Tools) ist das ein Security-Issue.

**Loesung:** Komplett automatisierbar via n8n Public API + n8n-mcp-Tools. Kein Klick in UI noetig.

## Schritt 1: Bearer-Credential via Public API anlegen

```python
import urllib.request, json, secrets

token = secrets.token_urlsafe(48)
api_key = "YOUR_N8N_API_KEY"

payload = json.dumps({
    "name": "My MCP Bearer Credential",
    "type": "httpBearerAuth",
    "data": {"token": token}
}).encode("utf-8")

req = urllib.request.Request(
    "https://<n8n-host>/api/v1/credentials",
    data=payload,
    headers={
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json"
    },
    method="POST"
)
with urllib.request.urlopen(req) as r:
    result = json.loads(r.read())
credential_id = result["id"]  # z.B. "idC1kOT9LEzjFFJe"
```

**Schema anfragen:** `GET /api/v1/credentials/schema/httpBearerAuth` — gibt `{token: string}` als einziges Pflichtfeld.

**Einschraenkung:** `GET /api/v1/credentials` gibt 403 Forbidden — LIST ist nicht via Public API moeglich. Nur CREATE + DELETE per ID.

## Schritt 2: MCP-Trigger-Node auf Bearer-Auth umstellen (pro Workflow)

Via `n8n-mcp` Tool `n8n_update_partial_workflow`:

```json
{
  "id": "<workflow_id>",
  "operations": [{
    "type": "updateNode",
    "nodeName": "<Name of MCP Trigger Node>",
    "updates": {
      "parameters.authentication": "bearerAuth",
      "credentials.httpBearerAuth": {
        "id": "<credential_id>",
        "name": "<credential_name>"
      }
    }
  }]
}
```

Mehrere Workflows in parallelen Calls updaten — lief bei 9 Workflows in einem Batch stabil durch.

## Schritt 3: Verifizieren via Endpoint-Probes

```python
import urllib.request, urllib.error

url = "https://<n8n-host>/mcp/<path>"

# Ohne Token: erwartet 403
req = urllib.request.Request(url, method="POST", data=b"", headers={"Content-Type":"application/json"})
try: urllib.request.urlopen(req)
except urllib.error.HTTPError as e: print(e.code)  # 403 Forbidden ✅

# Mit korrektem Token: erwartet 406 (Auth ok, aber MCP-Handler will 'Accept: text/event-stream')
req.add_header("Authorization", f"Bearer {token}")
try: urllib.request.urlopen(req)
except urllib.error.HTTPError as e: print(e.code)  # 406 Not Acceptable ✅ (= Auth durch)

# Mit falschem Token: erwartet 403
# ...
```

## Schritt 4: Token-Rotation (bei Kompromittierung)

1. Neuen Token generieren
2. `PUT /api/v1/credentials/<id>` mit `data: {token: "new_token"}`
3. Alle Client-Configs (.mcp.json, Claude Code Environment-Vars) aktualisieren

## Warum das interessant ist

- Kein n8n-UI-Klick noetig — skaliert auf 100+ Workflows
- Einheitliches Credential fuer alle MCPs vereinfacht Rotation
- Bearer-Auth ist Claude-Code-Connector-native (header: `Authorization: Bearer`)
- Schema wie `httpBearerAuth` wird von n8n's Credentials-API transparent unterstuetzt

## Gotchas

- `data` field beim Credential-Create NICHT vergessen (sonst wird Credential ohne Token angelegt)
- Bei Mass-Update: seriell besser als parallel (n8n hat Write-Locks auf Workflow-Ebene)
- Workflow-Backup nach Update neu ziehen — lokaler JSON-Stand muss mit n8n sync sein
- `credentials.httpBearerAuth` im Node-Update ist der exakte Key (nicht `.bearerAuth`)

## Quelle

- n8n Public API: https://docs.n8n.io/api/
- n8n-mcp Library: https://github.com/czlonkowski/n8n-mcp
- Anwendungsfall im Repo: `google-ads-agent/DECISIONS.md` (Phase 2), `docs/workflow-atlas.md` (Security-Status)
