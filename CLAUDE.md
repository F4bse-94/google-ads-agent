# google-ads-agent — Claude Kontext

Multi-Agent-System fuer woechentliches Google-Ads-Reporting nach Anthropic-Orchestrator-Worker-Pattern. Read-Only MVP, Cloud-scheduled via Claude Code Routines.

**MVP-Scope:** Read-Only Weekly Report per Email. Cloud-scheduled (z.B. Mo 07:00 Europe/Berlin).
**Nicht-Ziel MVP:** Chat-Interface, Write-Operations in Google Ads.

## Welten

| Welt | Pfad | Zweck |
|---|---|---|
| **Sub-Agent-Definitionen** | `.claude/agents/*.md` | Claude-Code-Sub-Agents mit YAML-Frontmatter, dispatched via Task-Tool |
| **Skills** | `skills/<name>/SKILL.md` | Filesystem-Skills, progressive disclosure, on-demand geladen |
| **Memory** | `memory/` | Git-Submodule auf `google-ads-memory` — Strategy, Findings-Log, Pending-Actions, Report-Historie |
| **Memory-Templates** | `templates/memory/` | Templates fuer neuen Account, kopieren in eigenes Memory-Repo |
| **Tools** | n8n-MCPs (8x Google Ads + 1x DataForSEO) + Helper (Memory-Bridge, GitHub-Helper, Mail-Bridge) | siehe `docs/workflow-atlas.md` |
| **Workflow-Engineering** | `n8n-mcp` (czlonkowski) via `.mcp.json` + Agent `n8n-workflow-engineer` | Build/Update/Validate der n8n-Workflows |
| **Routines** | `routines/*.md` | Claude Code Routine Configs (Prompt + Cron + Connectors) |

## Regeln

- **READ-ONLY Phase:** keine Google-Ads-Write-Operationen (keine `create_*`, `update_*`, `pause_*`, `remove_*`). Tools sind vorhanden aber werden nicht aufgerufen.
- **Strukturiertes Sub-Agent-Briefing:** Orchestrator uebergibt JSON-Struct mit `objective`, `output_schema`, `tools_available`, `boundaries`, `context_from_memory` (siehe `docs/handoff-contracts.md`). Kein Freitext.
- **Statistiker zieht eigene Rohdaten:** via GAQL/Reporting-MCPs. Kann Zeitfenster selbst waehlen (7d/14d/30d je nach Sample-Size).
- **Memory-Reads nur was der Intent braucht:** nicht alle Files bei jedem Run. `docs/report-anatomy.md` beschreibt welche Skill welche Memory-Files liest.
- **Report-Template ist fix:** `skills/weekly-report/template.md` — 12 Sektionen, Konsistenz ueber Wochen = Vergleichbarkeit.
- **Data-Freshness-Check:** jede Tool-Response enthaelt `data_timestamp`. Bei >36h Lag → Warning im Report.

## Architektur (Kurzform)

Orchestrator (Opus 4.7) → 4 parallele Sub-Agents (Performance-Analyst, Search-Keyword-Hunter, Statistiker, Market-Competitive) → Report-Composer (Sonnet 4.6) → GitHub-Commit + Gmail. Memory-Bridge schreibt deterministisch via GitHub-PAT (kein eigener AI-Agent dafuer). Details: `docs/architecture.md`.

## Anti-Patterns

- Workflow-JSONs in `workflows/` NIE direkt editieren — entweder via n8n-UI ODER via `n8n-workflow-engineer` Agent (n8n-mcp `n8n_update_partial_workflow`); danach lokales JSON-Backup ziehen
- `data.shared` beim Workflow-Backup entfernen
- Sub-Agents direkt anrufen ohne Struct-Briefing (fuehrt zu unfokussierten Outputs)
- Kein `CLAUDE.md`-Bloat — neue Inhalte in Skills/Docs, nicht hier

## Globale Regeln

- **n8n-Workflow-Konventionen:** `@.claude/rules/n8n-conventions.md`
- **Git:** `@.claude/rules/git-conventions.md`
- **Dokumentations-Standards:** `@.claude/rules/documentation-standards.md`
- **context7 Pflicht:** bei Fragen zu Bibliotheken/Frameworks/APIs immer zuerst context7 befragen
- **LEARNINGS update:** wenn ein Erkenntnis aufkommt, das in einer spaeteren Session nuetzlich ist → `docs/learnings/<slug>.md` + Index in `docs/LEARNINGS.md` aktualisieren

## Imports

@docs/architecture.md
@docs/LEARNINGS.md
