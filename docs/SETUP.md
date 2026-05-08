# Setup-Anleitung — google-ads-agent

Schritt-fuer-Schritt-Anleitung um das Multi-Agent-Reporting-System fuer einen eigenen Google-Ads-Account aufzusetzen. Lesezeit: ~30 min, Setup-Zeit: 2-4 Stunden (haengt davon ab wie viele Credentials du erstmals einrichtest).

> **Zielpublikum:** Marketing-Engineer / SEA-Manager mit n8n-Erfahrung. Kein Dev-Background noetig, aber Vertrautheit mit OAuth, API-Keys und Markdown.

---

## Inhaltsverzeichnis

1. [Voraussetzungen & Kosten](#1-voraussetzungen--kosten)
2. [n8n-Instanz vorbereiten](#2-n8n-instanz-vorbereiten)
3. [Repos klonen](#3-repos-klonen)
4. [Eigenes Memory-Repo aufsetzen](#4-eigenes-memory-repo-aufsetzen)
5. [Credentials in n8n einrichten](#5-credentials-in-n8n-einrichten)
6. [Workflows in n8n importieren](#6-workflows-in-n8n-importieren)
7. [.env und .mcp.json aufsetzen](#7-env-und-mcpjson-aufsetzen)
8. [Lokaler Test-Run mit Claude Code](#8-lokaler-test-run-mit-claude-code)
9. [Cloud-Routine konfigurieren](#9-cloud-routine-konfigurieren)
10. [Troubleshooting](#10-troubleshooting)
11. [Was kommt danach?](#11-was-kommt-danach)

---

## 1. Voraussetzungen & Kosten

### Accounts / Software

| Komponente | Wofuer | Kosten (Stand 2026) |
|---|---|---|
| **n8n self-hosted ≥ v1.104.0** | MCP-Server-Trigger via Streamable HTTP, AI-Agent-Workflows | ~7-30 EUR/Monat (Hetzner/DigitalOcean) ODER n8n Cloud ab 20 EUR/Monat |
| **GitHub-Account + 2 Repos** | Hauptrepo (`google-ads-agent`) + Memory-Repo (`google-ads-memory`) | Kostenlos (private Repos) |
| **Google Ads-Account + Developer Token** | Source-of-Truth fuer Reports | Kostenlos (nur Ad-Spend) |
| **Google Cloud Project** | OAuth-Client fuer Google Ads API | Kostenlos |
| **DataForSEO Account** | Keyword-Volumen, SERP, Competitor-Daten | Pay-as-you-go, ~50-100 USD/Monat fuer wenige Reports |
| **Claude Code (Anthropic Pro/Max/Team)** | lokale Werkstatt + Cloud-Routine-Scheduler | ab 20 USD/Monat (Pro) |
| **Anthropic API-Key** *(falls AI-Agent-Workflows in n8n direkt LLM aufrufen)* | LLM-Calls innerhalb n8n-Workflows | Pay-as-you-go nach Tokens |
| **Gmail-Account** | Versand der Executive Summary | Kostenlos |

### Pro-Run-Kosten (geschaetzt)

- ~3-5 USD pro Weekly-Report (Opus-Orchestrator + 4 Sonnet-Sub-Agents + Opus-Statistiker)
- DataForSEO: ~0.50-2 USD pro Report (Keyword-Volumen + SERP-Calls)

**Gesamt:** ~25-50 USD/Monat fuer 4 Wochenreports.

---

## 2. n8n-Instanz vorbereiten

### 2.1 Version pruefen

n8n muss **mindestens v1.104.0** sein, damit MCP-Server-Trigger via Streamable HTTP funktionieren. Aeltere Versionen koennen nur SSE und sind nicht kompatibel mit Claude Code Routines.

```bash
# In n8n-UI: oben rechts auf das Profil-Icon klicken, dann "Settings" → "About"
# Oder via API:
curl https://<your-n8n-host>/rest/instance | jq .version
```

Falls < 1.104.0: Update via Docker / npm / Pakete-Manager je nach Hosting.

### 2.2 n8n Public API aktivieren

Die `n8n-mcp`-Toolchain (czlonkowski) braucht Read+Write auf die Public API:

1. **Settings → n8n API → Create an API key**
2. Token kopieren — wird in `.env` als `N8N_API_KEY` benoetigt

### 2.3 Hostname / TLS

Die n8n-Instanz muss **per HTTPS oeffentlich erreichbar** sein, weil Claude Code Routines (in der Anthropic-Cloud) sonst keine MCP-Calls machen koennen.

- `https://<your-n8n-host>` muss von `claude.ai` aus erreichbar sein
- Self-signed Certs funktionieren NICHT — Let's Encrypt o.ae. ist Pflicht
- Falls hinter VPN / nur intern: alternativ Tailscale-Funnel oder Cloudflare-Tunnel

---

## 3. Repos klonen

### 3.1 Hauptrepo

```bash
git clone --recurse-submodules https://github.com/<your-user>/google-ads-agent.git
cd google-ads-agent
```

`--recurse-submodules` ist wichtig, damit das `memory/`-Submodule mitgezogen wird (auch wenn du es spaeter durch dein eigenes Memory-Repo ersetzt).

### 3.2 Repo-Struktur

```
google-ads-agent/
├── .claude/
│   ├── agents/           # 7 Sub-Agent-Definitionen
│   └── rules/            # Globale Konventionen (n8n, Git, Docs)
├── docs/                 # Architecture, Workflow-Atlas, Setup, Learnings
├── memory/               # Submodule auf eigenes Memory-Repo (siehe Step 4)
├── routines/             # Claude Code Routine Configs
├── scripts/              # Python-Stats-Helper (Referenz-Implementation)
├── skills/
│   └── weekly-report/    # Skill: SKILL.md + template.md + dispatch-playbook.md + references/
├── templates/
│   └── memory/           # Memory-Templates fuer eigenes Memory-Repo
├── workflows/            # 17 n8n-Workflow-Backups
├── .env.example          # Template fuer lokale Credentials (kopieren als .env)
├── .mcp.json.example     # Template fuer MCP-Server-Config (kopieren als .mcp.json)
├── CLAUDE.md             # Projektkontext fuer Claude Code
├── README.md             # Uebersicht
└── DECISIONS.md          # Architektur-Entscheidungen (historisch)
```

---

## 4. Eigenes Memory-Repo aufsetzen

Das Memory-Repo ist ein **separates GitHub-Repo**, das die Strategie und das Lern-Gedaechtnis des Multi-Agent-Systems speichert. Es wird vom Hauptrepo als Submodule referenziert.

### 4.1 Neues GitHub-Repo anlegen

Erstell ein neues, **privates** GitHub-Repo namens z.B. `<dein-user>/google-ads-memory`. **Nicht initialisieren** mit README/License — wir pushen leer.

### 4.2 Templates kopieren

```bash
# Im Hauptrepo:
cd google-ads-agent

# Templates kopieren in tmp-Ordner
cp -r templates/memory /tmp/my-memory-init
cd /tmp/my-memory-init

# Als neues Repo initialisieren
git init -b main
git add .
git commit -m "chore: initial memory repo from template"
git remote add origin https://github.com/<dein-user>/google-ads-memory.git
git push -u origin main
```

### 4.3 Strategy-Manifest befuellen

Oeffne `00_strategy_manifest.md` in deinem Memory-Repo und ersetze ALLE `<...>`-Platzhalter mit deinen Account-Spezifika:
- `<ACCOUNT_NAME>` — z.B. "Mein Account"
- `<CUSTOMER_ID>` — Google Ads Customer-ID (10-stellig, ohne Bindestriche, z.B. `1234567890`)
- `<LOGIN_CUSTOMER_ID_IF_MCC>` — falls dein Account unter einem MCC liegt: dessen ID. Sonst leer.
- Produkte, KPIs, Negatives, Kampagnen-Architektur — siehe Inline-Hinweise im Template

**Wichtig:** Sektion 5 (Negatives) und Sektion 6 (KPI-Schwellen) werden vom Multi-Agent **gelesen** — wenn die leer sind, gibt es keine sinnvolle Ampel-Logik im Report.

### 4.4 Submodule-Verweis im Hauptrepo umstellen

```bash
cd google-ads-agent

# Alte Submodule-Referenz entfernen
git submodule deinit memory
git rm memory
rm -rf .git/modules/memory  # falls noetig

# Neues Memory-Repo als Submodule hinzufuegen
git submodule add https://github.com/<dein-user>/google-ads-memory.git memory
git commit -m "chore(memory): point submodule to own memory repo"
```

---

## 5. Credentials in n8n einrichten

Du brauchst **6 Credential-Typen** in deiner n8n-Instanz. Lege sie unter Credentials → Add Credential an.

### 5.1 Google Ads OAuth

| Feld | Wert |
|---|---|
| Type | Google Ads OAuth2 API |
| Client ID | aus deinem Google Cloud Project |
| Client Secret | aus deinem Google Cloud Project |
| Developer Token | aus Google Ads → Tools & Settings → API Center |
| Scopes | `https://www.googleapis.com/auth/adwords` |

**Setup-Steps:**
1. Google Cloud Console → "OAuth consent screen" konfigurieren
2. APIs aktivieren: "Google Ads API"
3. Credentials → "OAuth 2.0 Client IDs" → Web application → Authorized redirect URIs: `https://<your-n8n-host>/rest/oauth2-credential/callback`
4. In Google Ads: API Center → Developer Token beantragen (Test-Token reicht fuer lokale Tests, fuer Production: Basic/Standard Access beantragen)
5. In n8n den OAuth-Flow durchklicken → "Sign in with Google"

### 5.2 DataForSEO Basic Auth

| Feld | Wert |
|---|---|
| Type | HTTP Basic Auth (in DataForSEO-Workflow) ODER Header Auth |
| Username | dein DataForSEO API Login |
| Password | dein DataForSEO API Password |

Login + Password gibt es nach Account-Anmeldung unter dataforseo.com → My APIs.

### 5.3 GitHub PAT (Personal Access Token)

Fuer Memory-Bridge-Schreibzugriff auf das Memory-Repo:

1. github.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Scope: `repo` (Full control of private repositories)
4. Token kopieren — kann **nur einmal** angezeigt werden

In n8n als **Header Auth Credential** anlegen:
- Name: `GitHub Memory PAT`
- Header Name: `Authorization`
- Header Value: `Bearer <dein-pat>`

### 5.4 HTTP Bearer Auth (Master-Token fuer MCPs)

Dieses Token sichert alle 9 MCP-Server-Endpoints in n8n. Gleicher Token fuer alle 9 — vereinfacht Rotation.

1. **Token generieren** (z.B. via `openssl rand -base64 48` oder beliebiger Password-Manager)
2. In n8n: Credentials → Add → "Header Auth"
3. Name: `Google Ads Agent MCP Bearer`
4. Header Name: `Authorization`
5. Header Value: `Bearer <dein-master-token>`

Das gleiche Token musst du **spaeter** in der `.mcp.json` (lokal) und im Claude Code Routine Connector-Setup hinterlegen.

### 5.5 Gmail OAuth (fuer Mail-Bridge)

Setup wie 5.1 (OAuth via Google Cloud), Scope: `https://www.googleapis.com/auth/gmail.send`.

### 5.6 OpenAI / Anthropic API Key (fuer AI Agent Workflows)

Die 6 AI-Agent-Workflows (12-17) nutzen `@n8n/n8n-nodes-langchain.lmChatOpenAi` oder Anthropic-Aequivalent. Default ist OpenAI-kompatibles GPT-Model.

| Feld | Wert |
|---|---|
| Type | OpenAI API |
| API Key | dein sk-... Token |

> **Hinweis:** Die AI-Agent-Workflows nutzen ein "Mixed-Mode"-Pattern: Hauptanalyse via primary LLM, Fallback-LLM via `needsFallback`-Toggle (siehe `docs/learnings/n8n-ai-agent-v3-1-features.md`). Du kannst beide Slots auf das gleiche Modell setzen — ist dann nur Resilienz gegen API-Outages.

---

## 6. Workflows in n8n importieren

Im Repo unter `workflows/` liegen 17 JSON-Backups.

### 6.1 Reihenfolge des Imports

| # | Workflow | Typ | Was es tut |
|---|---|---|---|
| 1-8 | `01-account-tools.json` ... `08-gaql-tools.json` | MCP-Server-Trigger | Google Ads API Tools (Account, Campaigns, Ad Groups, Ads, Keywords, Reporting, Insights, GAQL) |
| 9 | `09-dataforseo-mcp.json` | MCP-Server-Trigger | DataForSEO API Tools |
| 10 | `10-memory-bridge.json` | Webhook | Composer schreibt durch hier in das Memory-Repo |
| 11 | `11-github-memory-helper.json` | Sub-Workflow | GitHub-API-Wrapper mit Atomic-Edit-Pattern (Race-Condition-Schutz) |
| 12 | `12-sub-report-composer.json` | AI Agent | Report-Composer (Sonnet) |
| 13 | `13-sub-market-intelligence.json` | AI Agent | Market & Competitive (Sonnet) |
| 14 | `14-main-orchestrator.json` | AI Agent | Lead-Agent (Opus) — orchestriert Sub-Agents |
| 15 | `15-sub-performance-analyst.json` | AI Agent | Performance-Analyst (Sonnet) |
| 16 | `16-sub-search-keyword-analyst.json` | AI Agent | Search & Keyword-Hunter (Sonnet) |
| 17 | `17-sub-statistician.json` | AI Agent | Statistiker (Opus) |

### 6.2 Import-Schritte fuer jeden Workflow

1. n8n-UI → Workflows → Import from File → JSON-Datei auswaehlen
2. **VOR Speichern:** Customer-IDs ersetzen (nur in Workflows 1-8):
   - `<YOUR_CUSTOMER_ID>` → deine Google Ads Customer-ID (z.B. `1234567890`)
   - `<YOUR_LOGIN_CUSTOMER_ID>` → deine Login-Customer-ID (MCC-ID, falls vorhanden)
3. **Credentials zuweisen:**
   - Google Ads OAuth → bei allen HTTP-Request-Nodes mit Google Ads URLs
   - DataForSEO Auth → in Workflow 9
   - HTTP Bearer Auth (Master-Token) → in jedem MCP-Server-Trigger (Workflows 1-9, im Trigger-Node "Authentication: Bearer")
   - GitHub Memory PAT → in Workflow 11 (HTTP-Request-Nodes mit GitHub-URLs)
   - Gmail OAuth → in Workflow `Mail-Bridge` (siehe Hinweis unten)
   - OpenAI/Anthropic → in den AI-Agent-Nodes (Workflows 12-17)
4. **Aktivieren:** Save → Toggle "Active" oben rechts

### 6.3 Mail-Bridge-Workflow

Mail-Bridge ist als separater MCP-Server gedacht (Workflow nicht im Repo, weil Gmail-OAuth-spezifisch). Build-Anleitung:

1. Neuer Workflow: "Mail-Bridge"
2. Trigger: MCP Server Trigger, Path: `mail-bridge`, Authentication: Bearer (gleicher Master-Token wie andere)
3. Tool-Node: "Gmail Send Email" mit OAuth-Credential
4. Aktivieren

Im `.mcp.json` als zusaetzlicher Server eintragen (siehe Step 7).

### 6.4 Workflow-Validierung via n8n-mcp

Falls du Claude Code lokal mit `.mcp.json` (siehe Step 7) konfiguriert hast, kannst du die Validation automatisieren:

```bash
claude
# In Claude Code:
> Use the n8n-workflow-engineer agent to validate all 17 imported workflows
```

Oder manuell pro Workflow:
- Trigger-Node testen ("Execute Node")
- Tool-Listing pruefen: `curl -H "Authorization: Bearer <token>" https://<your-n8n-host>/mcp/<path>`

---

## 7. .env und .mcp.json aufsetzen

### 7.1 .env

```bash
cp .env.example .env
# Editor oeffnen und Werte eintragen
```

Inhalt:
```bash
# n8n Public API (fuer n8n-mcp-Tool zur Workflow-Verwaltung)
N8N_API_KEY=<aus n8n Settings → API → Create API Key>
N8N_BASE_URL=https://<your-n8n-host>

# Optional: GitHub PAT fuer lokale Memory-Reads (falls nicht via Submodule)
# GITHUB_MEMORY_PAT=ghp_xxx

# Optional: Anthropic API-Key fuer lokale Stats-Skripte
# ANTHROPIC_API_KEY=sk-ant-xxx
```

### 7.2 .mcp.json

```bash
cp .mcp.json.example .mcp.json
# Editor: alle <YOUR_N8N_HOST> + <YOUR_N8N_MCP_BEARER_TOKEN> ersetzen
```

Das File listet 9 MCP-Server (Google Ads + DataForSEO) plus n8n-mcp (npm-Tool fuer Workflow-Engineering). Nach Aenderung: Claude Code neu starten — die `.mcp.json` wird beim Start gelesen.

### 7.3 n8n-mcp installieren (optional, fuer Workflow-Engineering)

Wenn du Claude Code zum Bau/Update von Workflows nutzen willst:

```bash
npm install -g n8n-mcp@latest
```

(Hinweis: Beim Auto-Update via npx gab es 2026 wiederholt Issues — globale Installation ist robuster.)

---

## 8. Lokaler Test-Run mit Claude Code

### 8.1 Claude Code starten

```bash
cd google-ads-agent
claude
```

Das laedt die `.mcp.json` und stellt 9 MCP-Server bereit.

### 8.2 Smoke-Test: MCP-Connectivity

```
> List available MCP tools and show me which Google Ads MCPs respond.
```

Erwartetes Verhalten: Claude listet alle 9 MCP-Server, jede sollte Tools wie `list_campaigns`, `get_campaign`, etc. zeigen.

### 8.3 Trockentest: Performance-Analyst alleine

```
> Run the performance-analyst sub-agent for LAST_7_DAYS using a minimal briefing JSON. Save output to /tmp/test-perf.json.
```

Erwartetes Verhalten: Sub-Agent aus `.claude/agents/performance-analyst.md` wird via Task-Tool gestartet, ruft 5-8 MCP-Tools auf, gibt JSON zurueck.

### 8.4 Full-Run: Weekly Report

```
> Run the weekly-report skill for the current ISO week.
```

Dauer: 8-15 min. Erwartetes Verhalten:
1. Memory wird gelesen (`memory/00_strategy_manifest.md`, `memory/02_findings_log.md`)
2. 4 Sub-Agents laufen parallel (Task-Tool-Outputs sichtbar)
3. Report-Composer rendert Template
4. Report wird in `memory/reports/YYYY-WNN-report.md` geschrieben (lokales Submodule-Pendant — du kannst ihn pushen via `cd memory && git push`)
5. Falls Mail-Bridge konfiguriert: Email kommt an

### 8.5 Validation des Reports

Oeffne `memory/reports/<aktueller-iso-week>-report.md`. Pruefe:
- Sind alle 12 Sektionen befuellt? (Sektion 0-11)
- Stimmen die KPI-Zahlen mit Google Ads UI ueberein? (Spend, Conversions sollten match — Toleranz ±5% wegen Daten-Lag)
- Sind die Negative-Keyword-Kandidaten plausibel?
- Hat der Statistiker mindestens eine Hypothese getestet?

---

## 9. Cloud-Routine konfigurieren

Sobald lokaler Test laeuft: Setup der **Claude Code Routine** fuer wiederkehrende Cloud-Ausfuehrung. Komplette Anleitung: [routines/weekly-report.md](../routines/weekly-report.md).

Kurzform:

1. **claude.ai/settings/connectors** — Gmail + GitHub Connectors aktivieren
2. **9 Custom HTTP MCP Connectors** anlegen (gleiche URLs + Bearer-Token wie in `.mcp.json`)
3. **claude.ai/code/routines** → New routine
4. Repos: `<your-user>/google-ads-agent` + `<your-user>/google-ads-memory`
5. Prompt aus [routines/weekly-report.md](../routines/weekly-report.md) Abschnitt "Routine-Prompt" kopieren
6. Trigger: Schedule, Weekly Monday 07:00 Europe/Berlin
7. **Run now** klicken — Smoke-Test
8. Pruefen: GitHub-Commit im Memory-Repo? Email kam an?

---

## 10. Troubleshooting

| Symptom | Ursache | Loesung |
|---|---|---|
| `401 Unauthorized` auf MCP-Call | Bearer-Token in `.mcp.json` falsch oder abgelaufen | Token in n8n-Credential pruefen, `.mcp.json` updaten, Claude Code neu starten |
| Workflow zeigt keine Tools | MCP-Server-Trigger inaktiv | Workflow → Toggle "Active" oben rechts |
| `429 Too Many Requests` von Google Ads API | Rate-Limit | Sub-Agent-Prompts haben "Hard Caps" — pruefen ob jemand sie umgangen hat. Sonst: Developer-Token-Tier erhoehen |
| Statistiker liefert nur `insufficient_data` | Sample-Size zu klein bei kurzen Zeitfenstern | Statistiker erweitert automatisch auf 14d/30d/90d. Bei sehr neuem Account: warten bis genug Daten |
| Composer-Report ist leer in Sektion X | Sub-Agent X hat `DATA_UNAVAILABLE` zurueckgegeben | Session-URL oeffnen, Sub-Agent-Logs pruefen. MCP-Timeout? Tool-Cap erreicht? |
| GitHub-Commit-Fail im Memory-Bridge | PAT-Scope falsch oder Repo-Permissions | PAT muss `repo`-Scope haben; n8n muss Schreibrechte haben |
| Gmail-Send schlaegt fehl | OAuth-Scope fehlt | `gmail.send` Scope nachtragen, neu autorisieren |
| Custom-IDs `<YOUR_CUSTOMER_ID>` werden nicht ersetzt | Workflows nicht angepasst nach Import | Schritt 6.2 wiederholen — `<YOUR_CUSTOMER_ID>` und `<YOUR_LOGIN_CUSTOMER_ID>` in JSON-Editor in n8n ersetzen |
| n8n-mcp meldet `npx`-Errors | Globale Installation fehlt | `npm install -g n8n-mcp@latest`, dann in `.mcp.json` `command: "n8n-mcp"` (nicht `npx`) |

### Debug-Mode aktivieren

```bash
# In .env
DEBUG=1
LOG_LEVEL=debug

# Claude Code starten mit Verbose-Logging
claude --debug
```

### Logs anschauen

- **n8n-Workflows:** Executions-View pro Workflow → "View" → Step-fuer-Step JSON-Outputs
- **Claude Code lokal:** `~/.claude/logs/` (je nach OS)
- **Cloud-Routine:** [claude.ai/code/sessions](https://claude.ai/code/sessions) → Routine-Run anklicken → Vollstaendiges Transcript

---

## 11. Was kommt danach?

### Iterieren am Report

Nach 2-3 Wochen-Reports wirst du sehen, wo die Schwachstellen liegen:
- **Zu generische Empfehlungen?** → Sub-Agent-Prompt schaerfen (`.claude/agents/<name>.md`)
- **Statistiker-Hypothesen drueben?** → Default-Hypothesen in `statistician.md` anpassen
- **Negatives haeufen sich?** → Strategy-Manifest Sektion 5.2 manuell konsolidieren

Aenderungen pushen, dann naechster Run nutzt sofort die neuen Prompts.

### Write-Operationen aktivieren (Phase 2)

Aktuell `READ_ONLY = true`. Wenn das Vertrauen in das System steht:

1. Sub-Agent fuer "Action-Apply" hinzufuegen (z.B. `negative-keyword-applier.md`)
2. Approval-Gate: Email mit "Apply yes/no?" → Reply triggert Routine mit Write-Mode
3. Audit-Log in Memory mit jedem Apply

Roadmap-Skizze: siehe [DECISIONS.md](../DECISIONS.md).

### Mehrere Accounts / Multi-Tenant

Pro Account: eigenes Memory-Repo + eigene Routine + (optional) eigener n8n-Workflow-Set falls Customer-IDs in Workflows hardcoded sind. Cleaner Long-Term: Customer-ID als Routine-ENV-Var, n8n-Workflows lesen sie dynamisch.

### Cost-Optimierung

- Sub-Agent-Modelle pruefen — laeuft Statistiker auch mit Sonnet? (Test-Cycles, dann downgraden)
- Caching auf MCP-Server-Ebene (n8n hat kein natives Cache, aber ein simpler Cache-Workflow vor MCP-Trigger ist machbar)
- Tool-Caps senken in Sub-Agent-Prompts wenn Reports konsistent unter Cap bleiben

---

## Verwandte Dokumente

- [README.md](../README.md) — Projekt-Uebersicht
- [DECISIONS.md](../DECISIONS.md) — Architektur-Entscheidungen, historisch
- [docs/architecture.md](architecture.md) — Detailtiefe der Multi-Agent-Topologie
- [docs/workflow-atlas.md](workflow-atlas.md) — Welcher Workflow macht was, mit Endpoints
- [docs/handoff-contracts.md](handoff-contracts.md) — JSON-Schemas der Sub-Agent-Outputs
- [docs/report-anatomy.md](report-anatomy.md) — 12-Sektionen-Template-Logik
- [docs/LEARNINGS.md](LEARNINGS.md) — Index aller dokumentierten Erkenntnisse
- [routines/weekly-report.md](../routines/weekly-report.md) — Cloud-Routine-Setup-Detail
- [templates/memory/README.md](../templates/memory/README.md) — Memory-Repo-Struktur

---

*Bei Problemen oder Fragen: Issue im Repo oeffnen oder Maintainer ansprechen.*
