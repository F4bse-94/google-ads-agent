---
name: Multi-Agent Orchestrator-Worker mit Struct-Briefings
description: Anthropic-Pattern fuer robuste Multi-Agent-Orchestrierung. Struct-JSON statt NL-Prompts zwischen Agents. 90% Performance-Gain laut Research.
type: reference
---

# Multi-Agent Orchestrator-Worker mit Struct-Briefings

**Problem aus der Praxis:** In einem frueheren Multi-Agent-System (Langdock, Google-Ads-SEA) fuehrten Natural-Language-Prompts vom Orchestrator an Sub-Agents zu fehlinterpretierten Ableitungen. Der Statistiker bekam z.B. Text wie "Schau dir mal die Mobile-Performance an" und machte dann beliebige Tests ohne klare Null-Hypothese oder Zeitfenster.

**Anthropic-Research-Erkenntnis:** Orchestrator-Worker mit **Opus-Lead + Sonnet-Workers** + strikt strukturierte Briefings liefern 90% Performance-Gain gegenueber Single-Agent-Setups bei Research-Tasks.

Quelle: https://www.anthropic.com/engineering/multi-agent-research-system

## Das Briefing-Schema

Jedes Task-Tool-Dispatch an einen Sub-Agent folgt **diesem JSON-Struct**, nicht einem Freitext-Prompt:

```json
{
  "briefing_id": "<uuid>",
  "orchestrator_run_id": "<session>",
  "timestamp": "<ISO-8601>",
  "agent": "<sub-agent-name>",
  "objective": "<1-2 Satz klares Ziel, messbar>",
  "output_schema": { "ref": "path-to-schema.md#contract-N" },
  "tools_available": ["<explicit-tool-names>"],
  "boundaries": {
    "time_window": "<domain-specific-parameter>",
    "read_only": true,
    "do_not": ["<verbotene-actions>"]
  },
  "context_from_memory": {
    "strategy_constraints": [...],
    "open_items_from_last_session": [...]
  }
}
```

## Warum das so wichtig ist

| Problem mit NL-Briefing | Mitigation durch Struct |
|---|---|
| Sub-Agent missinterpretiert Scope | `boundaries.time_window` explizit |
| Sub-Agent macht unerwartete Write-Calls | `boundaries.read_only: true` + `do_not: [...]` |
| Sub-Agent uebergibt unstrukturierten Output, Composer muss parsen | `output_schema` verweist auf JSON-Schema |
| Sub-Agent ignoriert vorherige Session-Findings | `context_from_memory.open_items_from_last_session` |
| Sub-Agent nutzt falsches Tool | `tools_available` als Whitelist |

## Sub-Agent-Response-Schema

Jeder Sub-Agent liefert strukturiertes JSON zurueck, NICHT Prose:

```json
{
  "agent": "<self>",
  "generated_at": "<ISO-8601>",
  "time_window_used": { "start", "end", "days", "adapted": true },
  "data_quality": {
    "timestamp_of_latest_data": "<ISO>",
    "hours_of_lag": <number>,
    "missing_data_warnings": []
  },
  "findings": [/* domain-specific */]
}
```

Composer-Phase (Synthesis) konsumiert dann N solcher JSONs und rendert Template-basiert.

## Pattern-Implementierung in Claude Code

In `.claude/agents/orchestrator.md`:
```markdown
## Sub-Agent-Dispatch (PARALLEL via Task-Tool)

Jedes Briefing folgt dem Schema aus `docs/handoff-contracts.md`. Kein Freitext.

| Sub-Agent | Wann dispatchen |
|---|---|
| performance-analyst | IMMER bei Weekly Report |
| statistician | bei jedem Weekly Report (mit eigenem MCP-Zugriff) |
...
```

In `.claude/agents/statistician.md`:
```markdown
## Input

JSON-Briefing vom Orchestrator mit:
- `hypotheses_to_test`: Liste von Hypothesen
- `boundaries.time_window_default`
- `context_from_memory.open_items_from_last_week`: Hypothesen die re-validiert werden sollen
```

## Besonderheit: Statistiker mit eigenem Daten-Zugriff

Ein Sonder-Pattern, das sich bewaehrt hat: **Der Statistiker bekommt keine Daten vom Orchestrator durchgereicht, sondern MCP-Zugriff und zieht selbst die Rohdaten.**

Vorteile:
- Orchestrator muss keine Daten pre-processen (die bei komplexen Tests falsch aggregiert sein koennten)
- Statistiker kann Zeitfenster adaptiv waehlen (7d → 14d → 30d → 90d bei Sample-Size-Problemen)
- Isolierter Kontext fuer statistische Reasoning-Ketten

Anti-Pattern: "Orchestrator gibt Statistiker ein Excel-Blob und fragt 'ist das signifikant?'" → fuehrt zu flachen Tests, ignoriert Sample-Size, keine Multiple-Testing-Korrektur.

## Parallele Ausfuehrung

Claude Code's Task-Tool handlet Parallel-Dispatch automatisch wenn der Orchestrator mehrere Task-Aufrufe in einem Prompt macht. Isolierte Kontexte pro Sub-Agent → 4 Sub-Agents parallel statt sequentiell reduziert Latenz um ~60%.

## Quellen

- Anthropic "How we built our multi-agent research system" (2025)
- Claude Code Sub-Agents Docs: https://code.claude.com/docs/en/agent-teams
- Anwendung im Repo: `google-ads-agent/docs/handoff-contracts.md`, `.claude/agents/*.md`, `skills/weekly-report/dispatch-playbook.md`
