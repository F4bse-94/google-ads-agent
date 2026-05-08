# Learnings Index

Dokumentierte Erkenntnisse fuer google-ads-agent. Jedes Learning ist eine Datei unter `docs/learnings/<slug>.md`.

**Prinzip**: Wenn in einer Session etwas erarbeitet wurde, das in einer zukuenftigen Session nuetzlich ist — hier eintragen.

## Claude Code Routines & MCPs

- [Claude Code Routines — Gotchas & Limitations](learnings/claude-code-routines-gotchas.md) — Connectors via UI (nicht .mcp.json), Submodule nicht auto-init, min. 1h Cron, Branch-Push-Default `claude/*`
- [n8n MCP Streamable HTTP Endpoints](learnings/n8n-mcp-streamable-http-endpoints.md) — URL-Struktur `/mcp/<path>` (nicht mehr `/sse`), Probe-Verhalten, `.mcp.json`-Format mit headers
- [n8n MCP Trigger Bearer-Auth automatisieren](learnings/n8n-mcp-trigger-bearer-auth.md) — Credential-Create via Public API + `update_partial_workflow` fuer alle Trigger in einem Rutsch

## Google Ads API & Query-Handling

- [Google Ads API v20 Auction Insights Workaround](learnings/google-ads-api-v20-auction-insights.md) — `auction_insight_domain` existiert nicht mehr, Fallback via `campaign_performance` IS-Felder + DataForSEO SERP
- [Google Ads n8n-MCP Standard-Queries haben Luecken](learnings/google-ads-mcp-default-queries-gaps.md) — IS, QS, match_type, all_conversions muessen manuell in Query-Body ergaenzt werden

## Multi-Agent-Architektur

- [Multi-Agent Orchestrator-Worker mit Struct-Briefings](learnings/anthropic-multi-agent-struct-briefing.md) — JSON-Struct statt NL-Prompts zwischen Agents (90% Perf-Gain laut Anthropic Research)
- [Statistiker-Agent mit eigenem MCP-Zugriff](learnings/statistician-with-own-mcp-access.md) — Anti-Pattern vermeiden: nicht durchreichen, sondern Hypothesen + adaptives Zeitfenster

## n8n-Workflow-Patterns (KW18 Post-Mortem, 2026-05-08)

- [GitHub-Edit Race-Condition + Atomic-Edit-Code-Node](learnings/github-edit-race-condition-atomic-pattern.md) — parallele SHA-Konflikte loesen via Code-Node mit Re-Fetch-Loop statt 3-Node-Chain
- [Code-Node hat kein httpRequestWithAuthentication — Helper-Webhook-Pattern](learnings/code-node-no-httpRequestWithAuthentication.md) — n8n 2.35.x Sandbox-Limit; Auth-Calls via Sub-Workflow-Webhook; localhost-URL gegen NAT-Loopback (KW19-Recovery)
- [n8n AI Agent Node v3.1 — Fallback-LLM, Batch Processing, Streaming](learnings/n8n-ai-agent-v3-1-features.md) — `needsFallback` + 2. LLM-Connection ersetzt manuelle Branch-Logik; Batch-Processing fuer Tool-Rate-Limits; Memory nur fuer Chat-Mode noetig
- [n8n Format-Code recursive flatten](learnings/n8n-format-code-recursive-flatten.md) — verschachtelte GAQL-Responses brauchen recursive flatten, nicht 1-level
- [Budget-Pacing burn_rate/forecast Berechnung](learnings/google-ads-budget-pacing-burn-rate-calculation.md) — `budget_pacing` MCP liefert nur Rohdaten, abgeleitete Felder im Format-Code-Node berechnen
- [ad_performance: adStrength + RSA-Asset-Daten in 1 Call](learnings/google-ads-ad-performance-asset-data-included.md) — GAQL-Erweiterung fuer Sektion 5a/5c/5d; `adGroupId=0` failed
