---
name: n8n MCP Trigger Streamable HTTP Endpoints
description: Wie die URL-Struktur, Transport-Verhalten und Migration von SSE zu Streamable HTTP in n8n ab v1.104 funktioniert
type: reference
---

# n8n MCP Trigger Streamable HTTP Endpoints

**Ab n8n v1.104.0 (21.07.2025)** unterstuetzt der MCP Server Trigger Streamable HTTP — das von MCP-Spec seit 2025 empfohlene Transport (SSE ist deprecated).

## URL-Struktur

Fuer einen MCP-Trigger mit `parameters.path = "my-tools"`:

| Transport | URL | Status |
|---|---|---|
| Streamable HTTP | `https://<n8n>/mcp/my-tools` | empfohlen, default aktiv |
| SSE (deprecated) | `https://<n8n>/mcp/my-tools/sse` | in neueren Versionen 404 |

Claude Workspace und Claude Code Routines erwarten beide Streamable HTTP in der MCP-Connector-Config.

## Endpoint-Probe ohne echten MCP-Client

Fuer Troubleshooting ist es hilfreich, die Endpoints mit einem simplen POST zu testen:

```python
import urllib.request, urllib.error

for path in ["/mcp/my-tools", "/mcp/my-tools/sse"]:
    url = f"https://n8n.example.com{path}"
    req = urllib.request.Request(url, method="POST", data=b"",
                                 headers={"Content-Type":"application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        print(f"{path} -> HTTP {e.code}")
```

**Interpretation:**
| HTTP Code | Bedeutung |
|---|---|
| `400 Bad Request` auf `/mcp/<path>` | Endpoint existiert, erwartet valide MCP-Initialisierung — **Streamable HTTP aktiv** ✅ |
| `404 Not Found` auf `/mcp/<path>/sse` | SSE deprecated oder deaktiviert in dieser Version |
| `401/403` auf `/mcp/<path>` | Authentication konfiguriert, Endpoint reagiert |
| `406 Not Acceptable` mit Auth-Header | Auth durch, Handler braucht `Accept: text/event-stream` |

## Claude Code `.mcp.json` Format fuer Remote HTTP-Connections

```json
{
  "mcpServers": {
    "my-n8n-mcp": {
      "type": "http",
      "url": "https://n8n.example.com/mcp/my-tools",
      "headers": {
        "Authorization": "Bearer ${MCP_TOKEN}"
      }
    }
  }
}
```

- `type: "http"` → Streamable HTTP
- `type: "sse"` → Legacy SSE (vermeiden)
- Env-Var-Substitution `${VAR}` wird von Claude Code unterstuetzt

## Gotchas

- Wenn n8n-Version <1.104: nur SSE-Endpoint verfuegbar, aber Claude-Connector erwartet Streamable HTTP → SSE-Problem-Meldung
- Bei selbst-gehosteten n8n-Instanzen: version via `GET /rest/settings` NICHT verfuegbar (gibt nur Auth/Feature-Flags). Direkter Version-Check schwer — Fabian-Empfehlung: in UI unter Help > About nachsehen
- Streamable HTTP ist stateful — n8n setzt Session-Cookies. Queue-Mode mit mehreren Webhook-Replicas braucht Session-Affinity (alle `/mcp*`-Requests auf denselben Replica routen)

## Quelle

- n8n Docs MCP Server Trigger: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/
- PR #15454 (Streamable HTTP Support): https://github.com/n8n-io/n8n/pull/15454 (gemerged 18.07.2025, v1.104.0)
- Anwendung im Repo: `google-ads-agent/docs/workflow-atlas.md` (Probe-Ergebnisse), `google-ads-agent/.mcp.json`
