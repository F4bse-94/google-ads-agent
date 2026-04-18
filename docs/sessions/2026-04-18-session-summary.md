# Session Summary — 2026-04-18 (Samstag)

**Dauer:** ca. 6-8h | **Hauptthema:** Phase 6 Deploy der Weekly-Report-Routine | **Status Session-Ende:** System ist deploy-ready, Fabian muss Routine-Prompt + Setup-Skript in claude.ai noch einmal aktualisieren, dann ersten autonomen Run starten.

---

## Was erreicht wurde

### 1. Phase 6 Deploy-Vorbereitung (3 Blocker)
- **Path-Bug** im Routine-Setup: Symlink `memory/` → parallel geklonter Memory-Repo
- **Memory-Writer Source-of-Truth**: Composer schreibt nur Report + JSON-Payload, `scripts/memory_writer.py` macht alle 4 Memory-File-Updates deterministisch (keine Doppelungen mehr)
- **WoW-Verifikation**: Pflicht-Feld `data_quality.wow_verification` im Performance-Analyst-Output (beide Timestamps + both_successful), Composer flagged WOW_UNVERIFIED falls fehlt

Commits: `066e250` (im alten n8n-projects-Monorepo) — Repo-Split s. Punkt 3.

### 2. Security-Decision — Bearer-Auth auf n8n-MCPs deaktiviert (PoC)
claude.ai Custom Connector UI unterstuetzt keine statischen Authorization-Header (nur OAuth2 oder None). Zwei Alternativen:
- Bearer-Auth in n8n rausnehmen → MCPs oeffentlich zugaenglich (nur URL-Obscurity als Schutz)
- Cloudflare Worker Proxy mit Query-Param-Token (sauber, aber ~1-2h Arbeit)

**Entscheidung fuer PoC:** Bearer weg, offen fahren. Dokumentiert als **P0-Todo** in `next-session-todos.md` mit Frist "spaetestens 7 Tage nach erstem erfolgreichen Run". Favorisierter Langfrist-Pfad: Cloudflare Worker.

**Security-Implikation:** Wer die URLs `https://n8n.srv867988.hstgr.cloud/mcp/*` kennt, kann aktuell MVV Google Ads Daten lesen. URLs stehen im privaten Repo, aber kein Production-grade Schutz.

### 3. Repo-Split: google-ads-agent in eigenes Repo
Rationale: reifere Architektur als andere Projekte im n8n-projects-Monorepo (eigenes Memory-Repo als Submodule, Multi-Agent-System, Cloud-Routine), verdient eigenen Space.

- **Neues Repo:** [F4bse-94/google-ads-agent](https://github.com/F4bse-94/google-ads-agent) — Fresh-Commit-Strategie, keine History-Uebertragung
- **Lokaler Pfad:** `C:\Users\fabia\Documents\Claude Projects\google-ads-agent\` (Top-Level, neben n8n-projects)
- **Mitgenommen:** komplettes `google-ads-agent/`, relevante `.claude/rules/` (n8n, git, documentation), 7 Google-Ads-relevante Learnings in `docs/learnings/`
- **Alter Monorepo:** `F4bse-94/n8n-projects` hat google-ads-agent/ Ordner entfernt + Redirect-Hinweis in README

### 4. Mail-Bridge — erst Webhook, dann MCP (Architektur-Konsistenz)
**Problem:** claude.ai Gmail-Connector liefert nur `create_draft`, kein `send_email`. Executive-Summary des Weekly Reports landete als Entwurf statt direkt versendet.

**Entwicklung:**
1. Erst gebaut als reiner Webhook-Workflow (`sio56m2zxbOtSStz`, Path `/webhook/send-weekly-report`) mit Gmail-Node + OAuth2-Credential
2. Test: funktionierte nach OAuth2-Setup (`WuFfkaTplA3haMId`, private Gmail via OAuth — Service Account ging nicht wegen fehlender Domain-Wide-Delegation bei privatem Account)
3. **Umbau auf MCP-Architektur** auf Fabians Wunsch: neuer Workflow `MWsWFnQubZ1Z21QL`, Path `/mcp/mail-bridge`, `mcpTrigger` + `gmailTool` mit `ai_tool`-Connection, analog zu den 9 Google-Ads-MCPs
4. Composer-Prompt + SKILL.md entsprechend zurueck von curl-Call auf MCP-Tool-Aufruf

Commits: `bc9331d` (Webhook), `9f86d3a` (MCP-Refactor)
**Alter Webhook-Workflow bleibt inaktiv** in n8n — kann nach Verifikation der MCP-Version geloescht werden.

### 5. api-quirks.md — zentrale MCP-Issue-Reference
Erster Routine-Run deckte 4 API-Probleme auf, alle vom Orchestrator mit Fallbacks gehandled. Um Trial-and-Error pro Session zu vermeiden, 7 Quirks in `skills/weekly-report/references/api-quirks.md` zentralisiert:

1. `geographic_performance` HTTP 400 bei Custom-Range (DURING vs BETWEEN Issue)
2. GAQL-Date-Enums nur bis LAST_30_DAYS
3. `auction_insight_domain`-View in v20 entfernt
4. DataForSEO `keyword_suggestions` 128k-Token-Limit
5. MCP-Default-Queries haben Gaps (IS, QS, match_type, all_conversions fehlen)
6. WoW-Vergleich braucht 2 separate Calls (Pflicht-Verifikation)
7. Stream-Idle-Timeouts bei langen MCP-Calls

Sub-Agent-Prompts haben jetzt einen **"Pflicht-Lese am Session-Start"**-Abschnitt mit Verweis auf die relevanten QUIRK-IDs. Keine Inline-Duplizierung.

Commits: `f826986`

### 6. Composer-Robustheit (Post-Mortem Stream-Timeout)
Composer scheiterte im ersten Run mit `Stream idle timeout - partial response received` beim Rendern des ~36 KB Markdown-Reports. 4 Fixes:

1. **Background-Dispatch**: `run_in_background: true` (statt Foreground mit strengerem Client-Stream-Timeout)
2. **Split-Write**: Sektionen 0-6 als initial Write, 7-12 + MEMORY_UPDATE_PAYLOAD als Append. Halbiert Write-Parameter-Groesse, plus Redundanz (Teil A persistiert auch wenn Teil B scheitert)
3. **Briefing-Straffung**: Sub-Agent-Outputs als File-Referenzen, Recommendations-Schema ausgelagert in neue `references/recommendations-priorisierung.md`
4. **Self-Fallback**: Orchestrator uebernimmt Komposition direkt bei Composer-Timeout, keine Rueckfrage

Plus: **Autonomie-Regel** explizit im Orchestrator ("keine Rueckfragen an Nutzer"), **ISO-Woche per `date +%V`** (nicht Eigenrechnung), **Collision-Check** fuer Report-Datei.

Commits: `78f5e09`

### 7. Symlink-Bootstrap-Bug (Runtime)
Setup-Script laeuft VOR dem Repo-Klon — Git klont danach und legt leeres `memory/` Submodule-Dir an, das den vorab gesetzten Symlink ueberschreibt. Fail-Fast-Check im Orchestrator stoppte den Run.

**Fix:** Symlink-Reset gehoert in den Orchestrator-Prompt als erster Bash-Command (zur Laufzeit, nach Git-Klon). Idempotent, keine Rueckfrage.

Commits: `37744ca`

---

## Offene Aktionen (Fabian muss manuell)

### 🔴 Blocking: Routine-Config in claude.ai aktualisieren

Der aktuelle Routine-Setup in claude.ai hat den **alten Stand** aus einer frueheren Session. Ohne diese Updates schlaegt jeder naechste Run fehl:

1. **Setup-Skript** → auf **nur** `pip install scipy statsmodels numpy` reduzieren. Die `rm -rf` + `ln -sfn` Zeilen raus — der Orchestrator macht das jetzt selbst zur Laufzeit.

2. **Orchestrator-Prompt** → komplett ersetzen durch den Stand aus `routines/weekly-report.md` (Abschnitt "Routine-Prompt"). Die Session-Chat-History hat den vollstaendigen Prompt als Copy-Paste-Block vom 2026-04-18 Abend.

3. **Speichern + Workflow aktiv lassen** — Save triggert in n8n die Production-Config-Neu-Ladung.

### 🟡 Optional: alten Webhook-Mail-Bridge loeschen
n8n-Workflow `sio56m2zxbOtSStz` ("Mail Bridge — Weekly Report Delivery") wurde ersetzt durch MCP-Version `MWsWFnQubZ1Z21QL`. Der alte bleibt als Fallback-Option inaktiv liegen. Nach erstem erfolgreichen Run mit MCP-Mail-Bridge kann er geloescht werden.

---

## Stand der Infrastruktur (Ende Session)

| Komponente | Status | Ort |
|---|---|---|
| google-ads-agent Repo | ✅ live | [F4bse-94/google-ads-agent](https://github.com/F4bse-94/google-ads-agent), lokal `c:\Users\fabia\Documents\Claude Projects\google-ads-agent\` |
| google-ads-memory Repo | ✅ live (als Submodule verknuepft, lokal via Submodule, Cloud via Symlink) | [F4bse-94/google-ads-memory](https://github.com/F4bse-94/google-ads-memory) |
| n8n Google-Ads MCPs (8x) | ✅ aktiv, Bearer-Auth **deaktiviert** (PoC-Risk) | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-*-tools` |
| n8n DataForSEO MCP | ✅ aktiv, Bearer-Auth deaktiviert | `https://n8n.srv867988.hstgr.cloud/mcp/dataforseo-mcp-v2` |
| Mail-Bridge MCP | ✅ aktiv, kein Bearer | `https://n8n.srv867988.hstgr.cloud/mcp/mail-bridge` (Workflow `MWsWFnQubZ1Z21QL`) |
| Gmail OAuth2 Credential in n8n | ✅ `WuFfkaTplA3haMId` fuer `fabian.smog@googlemail.com` | n8n Credentials |
| claude.ai Connectors | ✅ 10 drin (Gmail, GitHub, 8 Google-Ads, DataForSEO, Mail-Bridge) — **Prompt/Setup-Skript muss noch updated werden!** | claude.ai/settings/connectors |
| Claude Code Routine | ⚠️ angelegt aber Prompt/Setup-Skript auf veraltetem Stand | claude.ai/code/routines |
| Letzter Report im Memory-Repo | KW16 (v2 committed 2026-04-17) | [google-ads-memory/reports/2026-W16-report.md](https://github.com/F4bse-94/google-ads-memory/blob/main/reports/2026-W16-report.md) |

---

## Was Claude in naechster Session als erstes checken sollte

1. **Hat Fabian den neuen Prompt + Setup-Skript in claude.ai reingekopiert?** Falls nein: Copy-Paste-Block aus `routines/weekly-report.md` bereitstellen.
2. **Hat der naechste Routine-Run autonom durchlaufen?** Check: GitHub `google-ads-memory/reports/2026-W<NN>-report.md`, Email-Postfach, Session-Log.
3. **Haben die Fixes gewirkt?** Insbesondere: Composer Split-Write (Teil A + B), Self-Fallback, Symlink-Bootstrap, api-quirks-Workarounds proaktiv angewendet.
4. **Falls Run erneut scheitert:** Post-Mortem und Fix analog zu heute.
5. **Falls Run erfolgreich:** Post-MVP-Priorisierung (P0 Security-Layer via Cloudflare Worker — das ist der nachster harte Meilenstein).

---

## Relevante Files (Pfade in google-ads-agent/)

| Datei | Zweck |
|---|---|
| `routines/weekly-report.md` | **Source of Truth** fuer Routine-Prompt + Setup-Skript (Fabian muss den in claude.ai manuell synchronisieren) |
| `.claude/agents/orchestrator.md` | Autonomie, Bootstrap, Self-Fallback, ISO-Woche — Referenz fuer manuelle/lokale Runs |
| `.claude/agents/report-composer.md` | Split-Write Pattern, Mail-Bridge-MCP-Call, Memory-SoT-Boundary |
| `.claude/agents/performance-analyst.md` | WoW-Verifikation Pflichtfeld, Pflicht-Lese api-quirks |
| `.claude/agents/statistician.md` | LAST_90_DAYS-Fix, Custom-Range-Regel |
| `.claude/agents/market-competitive.md` | api-quirks QUIRK-3/4/7 Pflicht-Lese |
| `.claude/agents/search-keyword-hunter.md` | api-quirks QUIRK-4/7 Pflicht-Lese |
| `skills/weekly-report/SKILL.md` | Phasen A-G mit Background-Dispatch + Split-Write-Dokumentation |
| `skills/weekly-report/references/api-quirks.md` | 7 MCP-Issues + Workarounds (Pflicht-Lese fuer Sub-Agents) |
| `skills/weekly-report/references/recommendations-priorisierung.md` | P0/P1/P2/P3-Schema + Ableitungs-Regeln |
| `docs/next-session-todos.md` | priorisierte Backlog-Liste |
| `docs/learnings/*` | 7 Google-Ads-relevante Learnings (API-v20, MCP-Quirks, Multi-Agent-Pattern, etc.) |
| `scripts/memory_writer.py` | Deterministisches Memory-Update-Script, parst MEMORY_UPDATE_PAYLOAD aus Report |

---

## Commit-History dieser Session (chronologisch)

```
37744ca  fix(bootstrap): Symlink-Reset im Orchestrator-Prompt statt Setup-Script
78f5e09  fix(composer): haerten gegen Stream-Idle-Timeouts (Post-Mortem KW16/17)
f826986  feat(references): api-quirks.md — zentrale MCP-Quirk-Referenz
9f86d3a  refactor(delivery): Mail-Bridge als MCP statt Webhook
bc9331d  feat(delivery): n8n Mail-Bridge Webhook statt Gmail-MCP
0a2b915  fix(statistician): LAST_90_DAYS existiert nicht in Google Ads API
0445739  fix(routine): update paths for standalone repo
ebf49b4  Merge remote-tracking branch 'origin/main'  (OAuth-Setup-Artefakt)
f16bbe2  chore: initial commit — extracted from n8n-projects monorepo
```

Plus im alten n8n-projects-Repo:
```
d9bbeea  chore: extract google-ads-agent into standalone repo
066e250  fix(google-ads-agent): harden phase 6 deploy — 3 blockers resolved
```
