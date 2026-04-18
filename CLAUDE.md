# google-ads-agent — Claude Kontext

Multi-Agent-System fuer MVV Enamic Ads (Google Ads Account `2011391652`). Nachfolger des Langdock-Systems (`Agentensysteme_N8N_Langdock/langdock-systems/sea-google-ads`), neu gedacht nach Anthropic-Orchestrator-Worker-Pattern und Claude Code Routines.

**MVP-Scope:** Read-Only Weekly Report per Email. Cloud-scheduled via Claude Code Routines (Mo 07:00 Europe/Berlin).
**Nicht-Ziel MVP:** Chat-Interface, Write-Operations in Google Ads.

## Welten

| Welt | Pfad | Zweck |
|---|---|---|
| **Sub-Agent-Definitionen** | `.claude/agents/*.md` | Claude-Code-Sub-Agents mit YAML-Frontmatter, dispatched via Task-Tool |
| **Systemprompts (portable)** | `agents/*/systemprompt.md` | Markdown-Prompts, auch in Langdock/n8n reuseable |
| **Skills** | `skills/<name>/SKILL.md` | Filesystem-Skills, progressive disclosure, on-demand geladen |
| **Memory** | `memory/` | Git-Submodule `google-ads-memory` — Strategy, Session-Log, Findings-Log, Negatives, Top-Performers, Report-Historie |
| **Tools** | n8n-MCPs (8x Google Ads + 1x DataForSEO) | siehe `docs/workflow-atlas.md` |
| **Routines** | `routines/*.md` | Claude Code Routine Configs (Prompt + Cron + Connectors) |

## Regeln

- **READ-ONLY Phase:** keine Google-Ads-Write-Operationen (keine `create_*`, `update_*`, `pause_*`, `remove_*`). Tools sind vorhanden aber werden nicht aufgerufen.
- **Strukturiertes Sub-Agent-Briefing:** Orchestrator uebergibt JSON-Struct mit `objective`, `output_schema`, `tools_available`, `boundaries`, `context_from_memory` (siehe `docs/handoff-contracts.md`). Kein Freitext.
- **Statistiker zieht eigene Rohdaten:** via GAQL/Reporting-MCPs. Kann Zeitfenster selbst waehlen (7d/14d/30d je nach Sample-Size).
- **Memory-Reads nur was der Intent braucht:** nicht alle 5 Files bei jedem Run. `docs/report-anatomy.md` beschreibt welche Skill welche Memory-Files liest.
- **Report-Template ist fix:** `skills/weekly-report/template.md` — 12 Sektionen, Konsistenz ueber Wochen = Vergleichbarkeit.
- **Data-Freshness-Check:** jede Tool-Response enthaelt `data_timestamp`. Bei >36h Lag -> Warning im Report.

## Architektur (Kurzform)

Orchestrator (Opus 4.7) -> 4 parallele Sub-Agents (Performance-Analyst, Search-Keyword-Hunter, Statistiker, Market-Competitive) -> Report-Composer (Sonnet 4.6) -> GitHub-Commit + Gmail. Memory-Writer als deterministisches Tool (nicht Agent). Details: `docs/architecture.md`.

## Anti-Patterns

- Workflow-JSONs in `workflows/` NIE direkt editieren — immer via n8n-UI, dann `backup-n8n-workflow` Skill
- `data.shared` beim Workflow-Backup entfernen
- Sub-Agents direkt anrufen ohne Struct-Briefing (fuehrt zu unfokussierten Outputs)
- Kein `CLAUDE.md`-Bloat — neue Inhalte in Skills/Docs, nicht hier

## Globale Regeln

- **n8n-Workflow-Konventionen:** `@.claude/rules/n8n-conventions.md`
- **Git:** `@.claude/rules/git-conventions.md`
- **Dokumentations-Standards:** `@.claude/rules/documentation-standards.md`
- **context7 Pflicht:** bei Fragen zu Bibliotheken/Frameworks/APIs immer zuerst context7 befragen
- **LEARNINGS update:** wenn ein Erkenntnis aufkommt, das in einer spaeteren Session nuetzlich ist -> `docs/learnings/<slug>.md` + Index in `docs/LEARNINGS.md` aktualisieren

## Origin

Dieses Repo wurde am 2026-04-18 aus dem Monorepo `F4bse-94/n8n-projects` (Unterordner `google-ads-agent/`) als eigenstaendiges Projekt extrahiert (Fresh-Commit-Strategie ohne History-Uebertrag). Begruendung: reifere Architektur mit eigenem Memory-Repo + Cloud-Routine, klare Trennung von anderen n8n-Automatisierungen.

## Imports

@memory/00_strategy_manifest.md
@docs/architecture.md
@docs/LEARNINGS.md
