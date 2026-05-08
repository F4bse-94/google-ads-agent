# google-ads-memory — Templates

Diese Templates legen die Struktur fuer ein eigenes `google-ads-memory`-Repo vor. Das Memory-Repo ist die Single Source of Truth fuer alles was zwischen Multi-Agent-Sessions persistent sein muss (Strategie, offene Hypothesen, P0/P1-Items, Wochen-Reports).

## Setup-Schritte fuer ein neues Memory-Repo

1. **Eigenes GitHub-Repo anlegen** — z.B. `<dein-username>/google-ads-memory` (privat empfohlen)
2. **Diese 4 Files (+ leerer `reports/`-Ordner) ins Repo kopieren:**
   ```
   00_strategy_manifest.md   (anpassen — Account-Spezifika eintragen)
   02_findings_log.md         (kann leer bleiben, Statistiker fuellt beim 1. Run)
   03_pending_actions.md      (leer)
   reports/.gitkeep           (leerer Ordner)
   README.md                  (diese Datei, anpassen)
   ```
3. **`00_strategy_manifest.md` befuellen** — alle `<...>`-Platzhalter durch deine Werte ersetzen
4. **GitHub Personal Access Token (PAT)** mit `repo`-Scope generieren — wird in n8n als Credential verwendet (siehe Hauptrepo-SETUP.md)
5. **Submodul-Verweis im Hauptrepo** auf dein neues Memory-Repo umstellen:
   ```bash
   cd google-ads-agent
   git submodule deinit memory
   git rm memory
   git submodule add https://github.com/<user>/<your-memory-repo>.git memory
   git commit -m "chore(memory): point submodule to own memory repo"
   ```

## Memory-Schema (v2)

| File | Zweck | Update-Logik |
|---|---|---|
| `00_strategy_manifest.md` | Globale Strategie: Account-Kontext, Produkte, Zielgruppen, KPI-Leitplanken, kontoweite Negatives | **Mensch-gesteuert.** Composer ergaenzt NUR Sektion 5.2 (Negatives) mit neuen High-Priority-Kandidaten (append-with-dedupe). |
| `02_findings_log.md` | Offene Hypothesen + Ergebnisse statistischer Validierung (IDs F-001, F-002, ...) | **Composer-managed.** Statistiker re-validiert `insufficient_data`-Items in spaeteren Sessions. |
| `03_pending_actions.md` | Offene P0/P1-Recommendations aus den letzten Wochenreports | **Composer-managed Rotation.** Mensch markiert mit `[x]` was umgesetzt wurde. |
| `reports/<iso_week>-report.md` | Weekly Reports (vollstaendige Daten-Wahrheit pro Woche) | **Composer schreibt.** 12-Sektionen-Template aus `google-ads-agent/skills/weekly-report/template.md`. |

## Zugriffs-Pattern (wer liest/schreibt was?)

- **Orchestrator (Lead-Agent):** Liest `00_strategy_manifest.md` + `02_findings_log.md` bei jedem Run
- **Statistiker:** Liest `02_findings_log.md` (fuer offene Hypothesen zur Re-Validation)
- **Report-Composer:** Liest `reports/<vorige-woche>.md` fuer Follow-Up-Sektion
- **Memory-Bridge (n8n Workflow 10):** Schreibt alle Updates nach Report-Generation via GitHub-PAT

## Nicht ins Memory-Repo

- API-Keys, Credentials, Tokens — leben in n8n-Credentials und in Claude Code Routine ENV-Vars
- Rohdaten-Exports aus Google Ads — das Repo ist Narrativ + Aggregate, nicht Raw Data
- Workflow-JSONs, Prompts, Skills, Sub-Agents — die liegen im Schwesterrepo `google-ads-agent`
