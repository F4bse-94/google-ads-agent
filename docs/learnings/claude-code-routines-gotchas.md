---
name: Claude Code Routines — Gotchas & Limitations
description: Research-Preview seit 14.04.2026. Cloud-Scheduled-Agents. Repos werden geklont, Submodule NICHT automatisch initialisiert. Connectors via claude.ai Settings, nicht .mcp.json.
type: reference
---

# Claude Code Routines — Gotchas & Limitations

**Claude Code Routines** (Research Preview seit 14.04.2026) sind Cloud-basierte Scheduled Agents: Anthropic-Infrastruktur klont deine Repos, fuehrt Prompts aus, bleibt aktiv auch wenn dein Laptop zu ist.

Fuer Automations-Use-Cases wie wochentliche Reports absolut mächtig — aber ein paar nicht-offensichtliche Gotchas:

## 1. `.mcp.json` im Repo wird NICHT automatisch geladen

Fuer **lokale** Claude-Code-Sessions wird `.mcp.json` im CWD + parent-dirs automatisch verarbeitet und die MCP-Server verbunden.

Bei Routines **nicht**: Die MCP-Connectors werden ueber `claude.ai/settings/connectors` eingerichtet (UI), nicht aus einer Repo-Datei geladen. Die `.mcp.json` im Repo ist dort nur Dokumentation.

**Konsequenz:** Jeden MCP-Server manuell als "Custom HTTP Connector" in claude.ai anlegen, mit URL + Authorization-Header. Fuer unsere 9 n8n-MCPs hiess das 9-mal manuell anlegen.

**Workaround fuer Token-Management:** Token in claude.ai als Environment-Variable `N8N_MCP_TOKEN` hinterlegen, in jedem Connector-Header referenzieren als `Authorization: Bearer ${N8N_MCP_TOKEN}`.

## 2. Git-Submodule werden NICHT automatisch initialisiert

Routine klont das Haupt-Repo. `git submodule update --init` passiert **nicht** automatisch.

Wenn deine Prompts Memory-Files erwarten, die via Submodule gemountet sind, findet die Routine sie nicht.

**Workaround:** Submodule-Parent und Submodule als **zwei separate Repositories** in der Routine-Config hinzufuegen. Beide werden dann geklont (parallel). Der Orchestrator-Prompt muss beide Pfade kennen.

Beispiel: `n8n-projects/google-ads-agent/memory/` verweist via Submodule auf `google-ads-memory`. In der Routine:
- Repo 1: `F4bse-94/n8n-projects` (main repo mit Prompts/Skills)
- Repo 2: `F4bse-94/google-ads-memory` (Memory, wird parallel geklont → `./google-ads-memory/`)

Der Orchestrator-Prompt liest dann `google-ads-memory/00_strategy_manifest.md` statt `memory/00_strategy_manifest.md`.

## 3. Minimum Cron-Intervall: 1 Stunde

Trotz Custom-Cron-Expression (`/schedule update`): alles unter 1 Stunde wird abgelehnt. Fuer Minuten-Intervalle → andere Loesung (z.B. n8n-Cron der die Routine via API-Trigger aufruft).

## 4. Branch-Push-Default: nur `claude/*`

Claude Code schreibt per Default nur in Branches mit Prefix `claude/`. Fuer Routine die in `main` committen soll (z.B. Memory-Updates): im Repo-Setting "Allow unrestricted branch pushes" aktivieren.

**Sicherheits-Implikation:** Wenn aktiviert, kann die Routine theoretisch alles pushen. Daher dedicated Memory-Repo statt Haupt-Codebase empfohlen.

## 5. Kein Permission-Prompt waehrend des Runs

Routines laufen "Autonom durch" — keine Rueckfragen, keine Approval-Dialogs. Das heisst:
- Sicherheits-sensitive Tool-Calls duerfen nur in Runtime wenn vorher gescopet
- `boundaries.read_only: true` im Sub-Agent-Briefing ist hier pflicht-muster
- Bei Fehler-Pfaden: Fallback-Logik im Prompt, keine "frag den User"-Option

## 6. API-Trigger zum manuellen On-Demand-Run

```bash
curl -X POST https://api.anthropic.com/v1/claude_code/routines/<routine_id>/fire \
  -H "Authorization: Bearer <token_von_routine>" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "manual context string"}'
```

Ideal fuer:
- Ad-hoc-Runs ausserhalb des Cron-Schedules
- Integration mit n8n oder anderen Automations (n8n-Workflow kann die Routine triggern)
- Slack-Slash-Command das eine Routine anstoesst

**Token-Management:** Routine-Token wird EINMAL gezeigt bei Generierung. Sicher speichern!

## 7. Cost & Daily-Cap

- Cost-Profil: Opus-Orchestrator + 4 Sonnet-Workers = ~3-5 USD pro Run fuer unseren Weekly Report
- Daily-Cap pro Account (Pro/Max/Team/Enterprise unterschiedlich). Bei Ueberschreitung: Routine-Runs werden bis zum naechsten Tag verschoben
- Max-Pattern fuer hohe Frequenz: Routines nicht fuer Sub-Sekunden-Latenz — das sind n8n-Webhooks

## 8. Debugging

- Past Runs: `claude.ai/code/routines/<id>` → "Past Runs"
- Jeder Run ist eine Session (`claude.ai/code/sessions/<id>`) mit vollem Log
- Bei Fehler: Session-URL oeffnen, Sub-Agent-Outputs inspizieren
- Prompts-Update geht nur im Routine-Edit (neue Run-Instanz uebernimmt dann den Update)

## 9. Skills aus dem Repo werden automatisch geladen

Wenn deine Routine ein Repo klont und dort liegt ein `skills/my-skill/SKILL.md` — Claude Code loaded das automatisch wenn im Prompt darauf referenziert wird. Genau wie lokal.

Das ist DER Grund warum wir das Skill-System fuer Weekly-Report ueberhaupt sinnvoll ist: Routine klont Repo → Skills sind da → Orchestrator-Prompt sagt "run weekly-report skill" → Claude Code findet und loadet progressive.

## Quellen

- Claude Code Routines Docs: https://code.claude.com/docs/en/web-scheduled-tasks
- Anwendung im Repo: `google-ads-agent/routines/weekly-report.md`
