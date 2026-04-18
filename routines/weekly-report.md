# Claude Code Routine — Weekly Google Ads Report

Setup-Anleitung + exakter Prompt-Text zum Copy-Paste in [claude.ai/code/routines](https://claude.ai/code/routines). Cloud-basierte Ausfuehrung, laeuft auch wenn dein Laptop aus ist.

## Was diese Routine tut

Jeden Montag 07:00 Europe/Berlin:
1. Klont `n8n-projects` (Repo mit Prompts/Skills) und `google-ads-memory` (Repo mit Strategy/Findings)
2. Dispatcht den `weekly-report`-Skill
3. Orchestrator triggert 4 parallele Sub-Agents (Performance, Search/KW, Statistiker, Market)
4. Report-Composer rendert 12-Sektionen-Markdown
5. Committet Report in `google-ads-memory/reports/`
6. Sendet Executive-Summary per Gmail an Fabian
7. Updated Memory-Files (session_log, findings_log, negatives, top_performers)

Dauer: ca. 8-15 Minuten pro Run. Cost: ~3-5 USD pro Run (Opus Orchestrator + 4 Sonnet Sub-Agents + Opus Statistiker).

---

## Setup-Checkliste (einmalig, vor erstem Run)

### 1. Connectors einrichten ([claude.ai/settings/connectors](https://claude.ai/settings/connectors))

**Gmail (Standard-Connector):** aktivieren. Scope: `send_email`.

**GitHub (Standard-Connector):** aktivieren. Scope: `repo` fuer `F4bse-94/google-ads-memory` (Write-Zugriff fuer Report-Commits + Memory-Updates).

**9 Custom HTTP MCP Connectors** (manuell hinzufuegen):

| Connector-Name | URL | Headers |
|---|---|---|
| google-ads-account | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-account-tools` | `Authorization: Bearer ${N8N_MCP_TOKEN}` |
| google-ads-campaigns | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-campaign-tools` | `Authorization: Bearer ${N8N_MCP_TOKEN}` |
| google-ads-ad-groups | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-ad-group-tools` | `Authorization: Bearer ${N8N_MCP_TOKEN}` |
| google-ads-ads | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-ad-tools` | `Authorization: Bearer ${N8N_MCP_TOKEN}` |
| google-ads-keywords | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-keyword-tools` | `Authorization: Bearer ${N8N_MCP_TOKEN}` |
| google-ads-reporting | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-reporting-tools` | `Authorization: Bearer ${N8N_MCP_TOKEN}` |
| google-ads-insights | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-insights-tools` | `Authorization: Bearer ${N8N_MCP_TOKEN}` |
| google-ads-gaql | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-gaql-tools` | `Authorization: Bearer ${N8N_MCP_TOKEN}` |
| dataforseo | `https://n8n.srv867988.hstgr.cloud/mcp/dataforseo-mcp-v2` | `Authorization: Bearer ${N8N_MCP_TOKEN}` |

Token `upkL5r84LOG8fTN2izhvq0EyWr1GkXN9lA_rwdUouSKmPJDS-5fuavkkl09i1Txq` (siehe `google-ads-agent/.mcp.json`). In claude.ai als Environment-Variable `N8N_MCP_TOKEN` hinterlegen, dann in den Connector-Headern referenzieren.

### 2. Routine erstellen ([claude.ai/code/routines](https://claude.ai/code/routines))

Neues Routine, Klick "New routine". Felder ausfuellen:

**Name:** `Weekly Google Ads Report — MVV Enamic`

**Prompt:** siehe [Abschnitt unten](#routine-prompt).

**Repositories** (zwei hinzufuegen):
- `F4bse-94/google-ads-agent` — Branch-Push: `claude/*` (Default, nicht aendern)
- `F4bse-94/google-ads-memory` — Branch-Push: `main` (Checkbox "Allow unrestricted branch pushes" aktivieren, damit Memory-Updates direkt auf main gehen)

**Environment:**
- Default Cloud Environment nutzen
- Setup-Script (nur Python-Deps — Symlink wird im Orchestrator-Prompt gesetzt, weil Setup-Script VOR dem Repo-Klon laeuft und der Submodule-Klon den Symlink sonst ueberschreiben wuerde):
  ```bash
  pip install scipy statsmodels numpy
  ```

  **Warum Symlink nicht hier?** Die Routine klont `google-ads-agent/` NACH dem Setup-Script. Da `memory/` in der `.gitmodules` als Submodule deklariert ist, legt Git ein leeres `memory/`-Dir an — das wuerde einen vorab gesetzten Symlink ueberschreiben. Deshalb macht der Orchestrator-Prompt den Symlink-Reset als ersten Bash-Befehl zur Laufzeit (idempotent). Siehe [Learning: Claude Code Routines Gotchas #2](../docs/learnings/claude-code-routines-gotchas.md#2-git-submodule-werden-nicht-automatisch-initialisiert).

**Connectors:** Alle 11 (Gmail + GitHub + 9 MCPs) aktivieren.

**Triggers:**
- Type: Schedule
- Frequency: Weekly, Monday 07:00 Europe/Berlin
- (Optional: zusaetzlich API-Trigger fuer manuelles On-Demand)

### 3. Token in claude.ai als Environment-Variable

`N8N_MCP_TOKEN` muss in claude.ai Settings > Environment (oder via Routine Environment) hinterlegt sein. Claude Code injiziert die dann in die Connector-Headers.

Alternativ: Token direkt im Connector-Header hardcoden (weniger elegant, aber funktioniert fuer MVP).

---

## Routine-Prompt

Dies ist der exakte Prompt-Text, den du in das Routine-Prompt-Feld kopierst. Er triggert den `weekly-report`-Skill mit dem richtigen Kontext.

```
Du bist der Orchestrator fuer das MVV Enamic Ads Weekly Report System.

VOR ALLEM ANDEREN: Arbeitsverzeichnis + Memory-Symlink sicherstellen (IDEMPOTENT, keine Rueckfragen).

```bash
cd google-ads-agent
# Submodule-Directory entfernen (falls durch Git-Klon angelegt) und durch Symlink ersetzen.
# memory/ ist als Submodule im Repo deklariert, aber Routines initialisieren Submodules nicht —
# das Dir ist deshalb leer und muss durch Symlink auf den parallel geklonten Memory-Repo ersetzt werden.
rm -rf memory 2>/dev/null
ln -sfn "$(realpath ../google-ads-memory)" memory
# Verify — wenn das File nicht gefunden wird, ist der Memory-Repo-Klon selbst fehlgeschlagen (nicht der Symlink)
ls -la memory/00_strategy_manifest.md || { echo "FATAL: google-ads-memory Repo nicht geklont"; exit 1; }
```

Keine Confirmation-Frage an den Nutzer — das ist Housekeeping, immer gleich, idempotent.

Starte JETZT den `weekly-report` Skill aus `skills/weekly-report/SKILL.md`.

Kontext:
- Aktuelle ISO-Kalenderwoche: automatisch aus System-Datum (Europe/Berlin)
- Account: MVV Enamic Ads (CID 2011391652)
- Memory-Root (ueber Symlink): `memory/` → `../google-ads-memory/`
- Agent-Definitionen: `.claude/agents/*.md`
- Skill-Library: `skills/`

Ablauf (aus SKILL.md, Phasen A-G):

A. Liese memory/00_strategy_manifest.md, memory/02_findings_log.md (offene Items), memory/reports/<previous-week>.md (wenn existiert)

B. Dispatche PARALLEL via Task-Tool:
   - performance-analyst (LAST_7_DAYS)
   - search-keyword-hunter (LAST_14_DAYS)
   - statistician (adaptiv 7-90 Tage, mit Default-Hypothesen + offenen Findings)
   - market-competitive (LAST_30_DAYS)

   Jeder bekommt ein strukturiertes JSON-Briefing gemaess `skills/weekly-report/dispatch-playbook.md`.

C. Sammle 4 Outputs, validiere Schema-Compliance gegen `docs/handoff-contracts.md`.

D. Dispatche report-composer mit zusammengefasstem Input.

E. Composer:
   - Rendert Template aus `skills/weekly-report/template.md`
   - Committet nach `google-ads-memory/reports/YYYY-WNN-report.md` (Branch: main)
   - Sendet Executive-Summary via Gmail-Connector `send_email` an `f.smogulla@gmail.com`

F. Memory-Updates (Composer schreibt direkt via Git):
   - `01_session_log.md`: append mit Rollover bei >12 Eintraegen
   - `02_findings_log.md`: append neue, update alte Hypothesen
   - `03_negatives.md`: append neue Hard Negatives (dedupliziert gegen bestehende)
   - `04_top_performers.md`: append statistisch bestaetigte

G. Finale Zusammenfassung zurueckgeben (Status, Report-Link, Memory-Changes-Summary).

WICHTIG:
- READ-ONLY auf Google Ads — keine create_/update_/pause_/enable_/remove_ Tools aufrufen
- Bearer-Token ist in ENV `N8N_MCP_TOKEN` — nicht hardcoden
- Bei MCP-Timeout: 2x Retry mit Backoff, dann `DATA_UNAVAILABLE`-Flag im Report-Abschnitt
- Sprachstil im Report: Deutsch, sachlich, keine Marketing-Floskeln
- Executive-Summary im Email-Body als HTML-Format (Abschnitt 0), mit Link auf den Full-Report in GitHub

Begin now.
```

---

## Trigger-Config

### Schedule-Trigger (Primaer)

- Frequency: **Weekly**
- Day: **Monday**
- Time: **07:00**
- Timezone: **Europe/Berlin**
- Stagger: default (Claude Code kann bis zu 10 Minuten spaeter starten — OK, Report muss bis 09:00 da sein, genug Puffer)

Custom-Cron falls noetig (via CLI `/schedule update`):
```
0 7 * * 1
```
(Min: 0, Hour: 7, Day-of-Month: *, Month: *, Day-of-Week: 1 = Monday)

### API-Trigger (Sekundaer, fuer manuelle Runs)

Bei Routine-Edit "Add another trigger" → API. Token generieren und sicher speichern.

Manueller Trigger dann via:
```bash
curl -X POST https://api.anthropic.com/v1/claude_code/routines/<routine_id>/fire \
  -H "Authorization: Bearer <routine_token>" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Run for ISO week 17 of 2026 manually"}'
```

---

## Test-Plan (vor erstem Production-Run)

### T1: Lokaler Test (ohne Routine)

Claude Code in `google-ads-agent/` oeffnen:
```bash
cd google-ads-agent
claude  # MCP-Server werden aus .mcp.json geladen
```

Prompt:
```
Run the weekly-report skill for ISO week 17 of 2026.
```

Erwartetes Verhalten:
1. Orchestrator liest Memory
2. Dispatcht 4 Sub-Agents (sichtbar in der Task-Tool-Ausgabe)
3. Sub-Agents geben JSON-Outputs zurueck
4. Composer rendert Report
5. Report erscheint in `memory/reports/2026-W17-report.md`
6. (Email wird nur getriggert wenn Gmail-MCP konfiguriert — sonst Warning)

### T2: Routine-Smoke-Test

Nach Routine-Setup: "Run now" in claude.ai/code/routines klicken. Nicht auf Cron warten.

Verify:
1. Session-URL oeffnen (claude.ai/code/sessions)
2. Logs pruefen: 4 Sub-Agents dispatched? Composer gestartet?
3. GitHub-Commit in `google-ads-memory`? Neue Datei in `reports/`?
4. Email kam an?

### T3: Full End-to-End (naechste Woche)

Erster geplanter Run am naechsten Montag. Fabian checkt Posteingang 07:15-07:30 Uhr.

Falls Fehler: Session-URL aus Routine-Detail-Page zeigt Traceback.

---

## Monitoring & Troubleshooting

### Wo Runs sehen
- **Alle Sessions:** [claude.ai/code/sessions](https://claude.ai/code/sessions)
- **Diese Routine:** [claude.ai/code/routines](https://claude.ai/code/routines) → Routine-Detail → "Past Runs"

### Typische Fehler

| Fehler | Ursache | Loesung |
|---|---|---|
| `401 Unauthorized` auf MCP-Call | Bearer-Token falsch oder abgelaufen | Token neu setzen im Connector und in ENV-Var. n8n-Credential updaten. |
| `MCP timeout` bei einem Sub-Agent | n8n-Server ueberlastet oder Netzwerk | 2x Retry ist built-in. Bei wiederholtem Fehler: n8n-Instanz-Health pruefen. |
| Gmail-Send schlaegt fehl | Gmail-Connector nicht aktiviert / Scope fehlt | Settings > Connectors > Gmail → `send_email` Scope nachtragen |
| GitHub-Commit-Fail | Branch-Push-Restriction | `google-ads-memory` Routine-Setting: "Allow unrestricted branch pushes" aktivieren |
| Report-Qualitaet unausgewogen | Prompt-Drift, Sub-Agent-Output inkonsistent | Session-URL oeffnen, Sub-Agent-Outputs pruefen. Ggf. Prompt-Refinement in `.claude/agents/<name>.md` |
| Kosten-Ueberlauf | Opus-Model zu oft aufgerufen | Sub-Agent-Modelle auf sonnet ueberpruefen in `.claude/agents/*.md` YAML-Frontmatter |

### Daily Allowance

Claude Code Routines haben eine tages-basierte Cap. Bei Ueberschreitung: Routine wartet bis zum naechsten Tag. Weekly-Report-Routine ist 1 Run/Woche → kein Thema.

### Manueller Fallback

Wenn Routine kaputt: Fabian oeffnet Claude Code lokal im `google-ads-agent/` Verzeichnis und ruft `Run the weekly-report skill` manuell auf. Funktionell identisch (nutzt `.mcp.json`).

---

## Aufwaerts-Kompatibilitaet (Post-MVP)

Wenn MVP stabil laeuft, koennen diese Erweiterungen als separate Routinen angelegt werden:

1. **Daily Anomaly Check** (Cron: werktags 08:00) — nur Statistiker + Composer, nur Anomalien in Slack/Email
2. **On-Demand Deep-Dive** (API-Trigger) — fuer Ad-hoc-Analysen via HTTP POST
3. **Monthly Strategy Review** (Cron: 1. Werktag des Monats 09:00) — Aggregation ueber 4 Wochen-Reports, Strategy-Manifest-Review-Kandidaten flaggen

Jede zusaetzliche Routine hat eigene `routines/<name>.md` Config-Datei hier.

---

## Wichtige Dateien (zur Referenz)

- `google-ads-agent/skills/weekly-report/SKILL.md` — Phasen-Ablauf Detail
- `google-ads-agent/skills/weekly-report/template.md` — Report-Struktur
- `google-ads-agent/skills/weekly-report/dispatch-playbook.md` — JSON-Briefings
- `google-ads-agent/.claude/agents/*.md` — 6 Sub-Agent-Definitionen
- `google-ads-agent/docs/handoff-contracts.md` — JSON-Output-Schemas
- `google-ads-agent/docs/workflow-atlas.md` — MCP-Endpoints + Security-Status
- `google-ads-memory/` — Repo mit Strategy, Findings, Negatives, Top-Performers, Reports

---

## Status-Historie dieser Routine

*(zu pflegen nach Deploy und ersten Runs)*

| Datum | Event | Notes |
|---|---|---|
| 2026-04-17 | Config erstellt | vor Deployment |
| | Deployed | |
| | First successful run | |
