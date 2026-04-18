---
name: weekly-report
description: Generiert den wochentlichen Google Ads Report fuer MVV Enamic Ads (CID 2011391652) — orchestriert 4 parallele Sub-Agents (Performance-Analyst, Search-Keyword-Hunter, Statistiker, Market-Competitive), synthesiert 12-Sektionen-Report-Markdown, committet nach GitHub und sendet Executive-Summary per Gmail. Nutze dies wenn der User "weekly report", "wochentliches reporting", "google ads wochenbericht" oder sinngemaess fragt, oder wenn eine Claude Code Routine mit scheduled Trigger startet.
---

# Weekly Report Skill

Haupt-Skill fuer den wochentlichen Google-Ads-Report. Aufruf durch Routine (Cron Mo 07:00) oder manuell ("Run weekly-report for ISO week X").

## Trigger-Voraussetzungen

1. `.mcp.json` lädt 9 MCP-Server (8 Google Ads + DataForSEO)
2. GitHub-MCP aktiv (fuer Memory-Commits)
3. Gmail-MCP aktiv (fuer Email-Versand)
4. Memory-Repo als Submodule (`memory/`) oder als zweiter Repo (Routine) verfuegbar

## Ablauf (7 Phasen)

### Phase A — Bootstrap (Orchestrator)

1. Orchestrator (`.claude/agents/orchestrator.md`) startet
2. Bestimmt ISO-Kalenderwoche (aus ENV `CURRENT_ISO_WEEK` oder aus System-Datum)
3. Liest Memory:
   - `memory/00_strategy_manifest.md` komplett
   - `memory/02_findings_log.md` (nur offene Items: Status `open | insufficient_data | trend_only`)
   - `memory/reports/<previous-week>-report.md` (falls vorhanden, nur Open-Items-Sektion)

### Phase B — Dispatch (4 parallele Sub-Agents via Task-Tool)

Parallel (wichtig fuer Geschwindigkeit + isolierte Kontexte):
- `performance-analyst` mit Briefing aus `dispatch-playbook.md#performance-analyst`
- `search-keyword-hunter` mit Briefing aus `dispatch-playbook.md#search-keyword-hunter`
- `statistician` mit Briefing aus `dispatch-playbook.md#statistician` (enthaelt offene Hypothesen aus findings_log)
- `market-competitive` mit Briefing aus `dispatch-playbook.md#market-competitive`

**Hypothesen-Generierung fuer Statistiker:** Orchestrator sammelt plausible Hypothesen aus:
1. Offene Items aus `02_findings_log.md`
2. WoW-Deltas die "groß" aussehen (>20% bei Spend/Conv, nur als Hypothese — Statistiker entscheidet ob signifikant)
3. Default-Hypothesen die jede Session getestet werden:
   - "Mobile CVR < Desktop CVR"
   - "CPA Kampagne A ≠ CPA Kampagne B" (wenn 2+ aktive)
   - "Broad-Match CVR < Phrase/Exact CVR"

### Phase C — Collect & Validate

Orchestrator sammelt 4 JSON-Outputs. Validiert Schema-Compliance. Bei Fehlern:
- Fehlende Pflichtfelder → `DATA_UNAVAILABLE`-Flag im Briefing an Composer
- `data_quality.hours_of_lag > 36` → Warning in Appendix

### Phase D — Synthesis (Report-Composer)

Orchestrator ruft `report-composer` mit zusammengefasstem Input (Schema aus `docs/handoff-contracts.md#report-composer-input`). Composer rendert Template.

### Phase E — Persist (Report + Memory-Writer, strikt getrennt)

Composer:
1. Schreibt `memory/reports/YYYY-WNN-report.md` inkl. `MEMORY_UPDATE_PAYLOAD`-JSON-Block am Ende
2. **Ruft `scripts/memory_writer.py` auf** (Bash, deterministisch, kein LLM) — das Script liest den JSON-Block und updated die 4 Memory-Files:
   - `01_session_log.md` (append mit Rollover bei > 12)
   - `02_findings_log.md` (append neue Hypothesen, update alte)
   - `03_negatives.md` (append neue Hard Negatives mit Deduplizierung)
   - `04_top_performers.md` (append statistisch bestaetigte)
3. `git add memory/reports/ memory/0*.md` + `git commit` + `git push` im memory-Repo

**Wichtig — Source-of-Truth-Regel:** Composer schreibt **nur** den Report-Markdown. Die 4 Memory-Files werden **ausschliesslich** vom Python-Script aktualisiert. Kein Composer-Inline-Write auf `01_session_log.md` etc. Begruendung: Deterministik + Dedup-Logik (z.B. Negatives-Dedup) ist im Script, nicht im LLM.

### Phase F — Email via Mail-Bridge MCP

Composer ruft den MCP `mail-bridge` auf, Tool `send_email` (n8n-Workflow-ID `MWsWFnQubZ1Z21QL`):

Parameters:
- `to` — default `f.smogulla@gmail.com`
- `subject` — `Weekly Google Ads Report — KW {{iso_week}} | Status: {{status_emoji}}`
- `body_html` — vollstaendiges HTML-Dokument, Executive Summary (Sektion 0) + Link zu GitHub-Report

- `MEMORY_UPDATE_PAYLOAD`-Block NICHT mit in die Email
- Bei MCP-Tool-Fehler: im Session-Log flaggen, kein Fallback (lieber klar als Draft-Confusion)

Begruendung: claude.ai Gmail-Connector bietet nur `create_draft`, nicht `send_email`. Die Mail-Bridge nutzt den n8n gmailTool-Node mit eigener OAuth-Credential. Architektur analog zu den 9 Google-Ads-MCPs.

### Phase G — Session-Summary

Orchestrator gibt finale Zusammenfassung zurueck:
```
Session: 2026-W17 completed
- Status: 🟡 YELLOW
- Report: memory/reports/2026-W17-report.md
- Email sent: f.smogulla@gmail.com
- Memory updates: 2 new findings, 5 new negatives (dedup), 0 top_performers, 1 session_log entry
- Duration: Xm Ys
```

## Zeitfenster-Defaults

| Sub-Agent | Default | Begruendung |
|---|---|---|
| performance-analyst | LAST_7_DAYS | Woechentlicher Rhythmus |
| search-keyword-hunter | LAST_14_DAYS | Search-Term-Stabilitaet braucht Volumen |
| statistician | LAST_7_DAYS adaptiv → bis 90d | Sample-Size-basiert |
| market-competitive | LAST_30_DAYS | DataForSEO-Daten sind langsamer |

## Fehler-Handling

- **MCP-Timeout bei einem Sub-Agent:** Retry 2x mit Backoff. Wenn weiterhin fail → `DATA_UNAVAILABLE`-Flag, Sektion im Report mit Warning.
- **Statistiker findet keine ausreichende Sample-Size:** Hypothese mit `insufficient_data` in Findings-Log, Section 8 listet Power-Warnings.
- **Gmail-Versand schlaegt fehl:** Report wird trotzdem in GitHub committed. Fabian kann Link manuell aus Session-URL abrufen. Retry durch manuellen `Run now` auf Routine moeglich.

## Output-Qualitaets-Checklisten (Composer-Self-Check)

Siehe `.claude/agents/report-composer.md` "Qualitaets-Checkliste".

## Progressive Disclosure

- Report-Template: `template.md` (daneben)
- Briefing-JSON-Beispiele: `dispatch-playbook.md` (daneben)
- KPI-Definitionen: `references/kpi-definitions.md`
- Statistische Tests: `references/statistical-tests.md`
- B2B-Saisonalitaet DE: `references/b2b-seasonality-de.md`
- MVV-Account-Kontext: `references/mvv-account-context.md`
- Ampel-Kriterien: `references/ampel-kriterien.md`
