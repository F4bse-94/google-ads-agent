# n8n Workflow Konventionen

## Workflow-Entwicklung

- **Template-First**: Vor dem Bau eines neuen Workflows IMMER `search_templates()` via n8n-mcp pruefen (~2700 Vorlagen)
- **Multi-Level Validation**: `validate_node(minimal)` -> `validate_node(full)` -> `validate_workflow()`
- **Never Trust Defaults**: Alle Node-Parameter explizit setzen
- **Batch Updates**: `n8n_update_partial_workflow` mit mehreren Operations in einem Call

## Workflow-JSON Handling

- Workflows werden in n8n UND lokal als JSON gespeichert (`workflows/*.json`)
- **NICHT** MCP-Tool-Ergebnisse indirekt weiterverarbeiten (temporaere Dateien gehen verloren)
- **Stattdessen**: n8n REST API direkt mit `X-N8N-API-KEY` Header aufrufen
- **Immer** `delete data.shared` vor dem Speichern (enthaelt User-Daten, nicht ideal fuer Backup)

## Subprojekt-Struktur

Jedes Subprojekt unter `<workspace>/<name>/` hat mindestens:
- `CLAUDE.md` — Projekt-Kontext
- `README.md` — Human-readable
- `DECISIONS.md` — Entscheidungs-Log
- `workflows/` — n8n-JSON-Exports
- `input/` — Daten fuer dieses Projekt
- Optional: `.claude/` fuer projekt-spezifische Assets
- Optional: `.mcp.json` fuer projekt-spezifische MCP-Server
