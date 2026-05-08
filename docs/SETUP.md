# Setup-Anleitung — google-ads-agent (n8n)

Schritt-fuer-Schritt-Anleitung um das komplette Multi-Agent-System in einer eigenen n8n-Instanz aufzusetzen. Lesezeit: ~30 min, Setup-Zeit: 2-4 Stunden (haengt davon ab wie viele Credentials du erstmals einrichtest).

> **Zielpublikum:** SEA-Manager mit n8n-Erfahrung. OAuth, API-Keys und JSON-Editing sollten dir vertraut sein.

---

## Inhaltsverzeichnis

1. [Voraussetzungen & Kosten](#1-voraussetzungen--kosten)
2. [Architektur-Ueberblick](#2-architektur-ueberblick)
3. [n8n vorbereiten](#3-n8n-vorbereiten)
4. [Repo klonen](#4-repo-klonen)
5. [Eigenes Memory-Repo aufsetzen](#5-eigenes-memory-repo-aufsetzen)
6. [n8n-Credentials einrichten](#6-n8n-credentials-einrichten)
7. [MCP-Tool-Workflows importieren](#7-mcp-tool-workflows-importieren)
8. [Agent-Team-Workflows importieren](#8-agent-team-workflows-importieren)
9. [Workflow-IDs zwischen Workflows verknuepfen](#9-workflow-ids-zwischen-workflows-verknuepfen)
10. [Customer-IDs in den Tool-Workflows anpassen](#10-customer-ids-in-den-tool-workflows-anpassen)
11. [Mail-Bridge anlegen (optional)](#11-mail-bridge-anlegen-optional)
12. [Test-Run](#12-test-run)
13. [Schedule aktivieren](#13-schedule-aktivieren)
14. [Troubleshooting](#14-troubleshooting)
15. [FAQ](#15-faq)

---

## 1. Voraussetzungen & Kosten

### Accounts / Software

| Komponente | Wofuer | Kosten (Stand 2026) |
|---|---|---|
| **n8n self-hosted ≥ v1.104.0** | MCP-Server-Trigger via Streamable HTTP, AI-Agent-Workflows v3.1, Tool-Workflow-Calls | ~7-30 EUR/Monat (Hetzner/DigitalOcean) ODER n8n Cloud ab 20 EUR/Monat |
| **GitHub Account + 2 Repos** | Hauptrepo (`google-ads-agent`, kannst du forken) + Memory-Repo (eigenes, privat) | Kostenlos |
| **Google Ads-Account + Developer Token** | Source-of-Truth fuer Reports | Kostenlos (nur Ad-Spend) |
| **Google Cloud Project** | OAuth-Client fuer Google Ads API | Kostenlos |
| **DataForSEO Account** | Keyword-Volumen, SERP, Competitor-Daten | Pay-as-you-go, ~50-100 USD/Monat |
| **Anthropic ODER OpenAI API-Key** | LLM-Calls in den AI-Agent-Workflows | Pay-as-you-go nach Tokens, ~3-5 USD pro Weekly-Run |
| **Gmail-Account** | Versand der Executive Summary | Kostenlos |

**Pro-Run-Kosten:** ~3-5 USD (LLM) + ~0.50-2 USD (DataForSEO). Bei 4 Reports/Monat: **~25-50 USD/Monat**.

---

## 2. Architektur-Ueberblick

```
                              n8n Instanz
                              ───────────
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Orchestrator (Workflow 14)                                     │
│  ├── Trigger: Chat ODER Schedule (Cron)                         │
│  ├── LLM: AI Agent v3.1 (Anthropic/OpenAI)                      │
│  └── Ruft als Sub-Workflow-Tools auf:                           │
│      ├── call_performance_analyst       → Workflow 15           │
│      ├── call_search_keyword_analyst    → Workflow 16           │
│      ├── call_statistician              → Workflow 17           │
│      ├── call_market_intelligence       → Workflow 13           │
│      ├── call_report_composer           → Workflow 12           │
│      ├── read_memory_file               → Workflow 10           │
│      ├── campaign_performance           → Workflow 06           │
│      └── execute_gaql                   → Workflow 08           │
│                                                                 │
│  Sub-Agenten (Workflows 12, 13, 15, 16, 17)                     │
│  ├── Trigger: executeWorkflow (vom Orchestrator gerufen)        │
│  ├── LLM: AI Agent v3.1                                         │
│  └── Rufen Tool-Workflows als Sub-Workflows auf:                │
│      ├── Workflow 06 (Reporting), 08 (GAQL), 07 (Insights)      │
│      ├── Workflow 09 (DataForSEO)                               │
│      └── Workflow 10 (Memory-Bridge fuer Read+Write)            │
│                                                                 │
│  Memory-Bridge (Workflow 10)                                    │
│  ├── Trigger: MCP-Server (auch von Orchestrator als Tool)       │
│  └── Sub-Workflow: Workflow 11 (GitHub-API-Wrapper)             │
│                                                                 │
│  GitHub-Memory-Helper (Workflow 11)                             │
│  ├── Trigger: executeWorkflow (von Memory-Bridge)               │
│  └── Code-Node: Atomic-Edit-Pattern gegen GitHub Contents API   │
│                                                                 │
│  MCP-Tool-Workflows (Workflows 01-09)                           │
│  ├── Trigger: MCP-Server (auch direkt von AI-Agenten gerufen)   │
│  └── HTTP-Request-Nodes auf Google Ads API / DataForSEO API     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │  GitHub Memory-Repo  │
                    │  (separates Repo,    │
                    │   privat empfohlen)  │
                    │  ├ strategy_manifest │
                    │  ├ findings_log      │
                    │  ├ pending_actions   │
                    │  └ reports/          │
                    └──────────────────────┘
```

**Zwei Wege wie Workflows verbunden sind:**
- **Sub-Workflow-Calls** (`Tool: Workflow`-Node oder `Execute Workflow`-Node): direkter Aufruf eines anderen Workflows ueber dessen n8n-ID
- **MCP-Server-Trigger**: Workflow stellt sich als MCP-Server zur Verfuegung — kann von externen Clients (z.B. Claude.ai) ueber HTTPS angesprochen werden. Im Setup hier nicht zwingend genutzt (alle Calls laufen intern ueber Sub-Workflows), aber die MCP-Trigger sind aktiv und erlauben optional externe Nutzung.

---

## 3. n8n vorbereiten

### 3.1 Version pruefen

n8n muss **mindestens v1.104.0** sein. Aeltere Versionen unterstuetzen den AI-Agent-Node v3.1 oder den Streamable-HTTP-MCP-Trigger nicht voll.

```bash
# In n8n-UI: oben rechts auf das Profil-Icon → "Settings" → "About"
# Oder via Public API:
curl https://<your-n8n-host>/rest/instance | jq .version
```

Falls kleiner: Update via Docker / npm / PaaS-Updater.

### 3.2 n8n Public API aktivieren (optional)

Nur noetig wenn du Workflows per CLI/Script bulk-aktualisieren willst:

1. **Settings → n8n API → Create an API key**
2. Token kopieren — kann in `.env` (lokal) als `N8N_API_KEY` eingetragen werden

### 3.3 HTTPS sicherstellen

Wenn du die MCP-Trigger spaeter extern nutzen willst (z.B. von Claude.ai aus): die n8n-Instanz muss per HTTPS oeffentlich erreichbar sein. Self-signed Certs funktionieren nicht — Let's Encrypt o.ae. ist Pflicht.

Fuer den reinen Internal-Run (Orchestrator und Sub-Agenten rufen sich gegenseitig nur ueber n8n-Sub-Workflows) reicht dein internes n8n-Setup.

---

## 4. Repo klonen

```bash
git clone https://github.com/<dein-user>/google-ads-agent.git
cd google-ads-agent
```

Submodul-Init (`memory/`) wird vermutlich fehlschlagen, weil der Submodul-Verweis auf einen Platzhalter zeigt. Das ist beabsichtigt — du verlinkst dein eigenes Memory-Repo in Schritt 5.

---

## 5. Eigenes Memory-Repo aufsetzen

Das Memory-Repo ist ein **separates GitHub-Repo**, das die Strategie und das Lern-Gedaechtnis des Multi-Agent-Systems speichert. Wird vom Hauptrepo als Submodule referenziert, von der Memory-Bridge ueber GitHub-API gelesen+geschrieben.

### 5.1 Neues GitHub-Repo anlegen

Erstelle ein neues, **privates** GitHub-Repo namens z.B. `<dein-user>/google-ads-memory`. **Nicht initialisieren** mit README/License — wir pushen leer.

### 5.2 Templates kopieren und committen

```bash
# Im Hauptrepo:
cd google-ads-agent

# Templates in tmp-Ordner kopieren
cp -r templates/memory /tmp/my-memory-init
cd /tmp/my-memory-init

# Als neues Repo initialisieren
git init -b main
git add .
git commit -m "chore: initial memory repo from template"
git remote add origin https://github.com/<dein-user>/google-ads-memory.git
git push -u origin main
```

### 5.3 Strategy-Manifest befuellen

Oeffne `00_strategy_manifest.md` in deinem Memory-Repo (auf GitHub-UI oder lokal) und ersetze ALLE `<...>`-Platzhalter:
- `<ACCOUNT_NAME>` — Name deines Google Ads Accounts
- `<CUSTOMER_ID>` — 10-stellige Kunden-ID, ohne Bindestriche (z.B. `1234567890`)
- `<LOGIN_CUSTOMER_ID_IF_MCC>` — falls dein Account unter einem MCC liegt: dessen ID. Sonst leer lassen.
- Produkte (Sektion 3), Zielgruppen (Sektion 4), Negatives (Sektion 5), KPI-Schwellen (Sektion 6) — siehe Inline-Hinweise im Template

Wichtig: Sektion 5 (kontoweite Negatives) und Sektion 6 (Ampel-Schwellen fuer GREEN/YELLOW/RED) werden vom Multi-Agent **gelesen**. Wenn die leer bleiben, gibt es keine sinnvolle Ampel-Logik im Report.

### 5.4 Submodul-Verweis im Hauptrepo umstellen

```bash
cd google-ads-agent

# Alte Submodule-Referenz entfernen
git submodule deinit memory
git rm memory
rm -rf .git/modules/memory

# Eigenes Memory-Repo als Submodule hinzufuegen
git submodule add https://github.com/<dein-user>/google-ads-memory.git memory
git commit -m "chore(memory): point submodule to own memory repo"
```

---

## 6. n8n-Credentials einrichten

Du brauchst **6 Credential-Typen** in deiner n8n-Instanz. Lege sie unter Credentials → Add Credential an. Jede ID/Name notieren — du brauchst sie beim Workflow-Import.

### 6.1 Google Ads OAuth2

| Feld | Wert |
|---|---|
| Type | Google Ads OAuth2 API |
| Client ID | aus deinem Google Cloud Project |
| Client Secret | aus deinem Google Cloud Project |
| Developer Token | aus Google Ads → Tools & Settings → API Center |
| Scope | `https://www.googleapis.com/auth/adwords` |

**Setup-Schritte:**
1. Google Cloud Console → "OAuth consent screen" konfigurieren (Scopes: adwords)
2. APIs aktivieren: "Google Ads API"
3. Credentials → "OAuth 2.0 Client IDs" → Web application → Authorized redirect URIs: `https://<your-n8n-host>/rest/oauth2-credential/callback`
4. In Google Ads: API Center → Developer Token beantragen (Test-Token reicht fuer eigene Accounts; Production: Basic/Standard Access beantragen)
5. In n8n den OAuth-Flow durchklicken → "Sign in with Google"

**Wichtig:** Der OAuth-Account muss Zugriff auf das Google Ads-Konto haben, ueber das du reporten willst.

### 6.2 DataForSEO HTTP Header Auth

DataForSEO nutzt Basic Auth — wir koennen es als Header Auth abbilden:

| Feld | Wert |
|---|---|
| Type | HTTP Header Auth |
| Header Name | `Authorization` |
| Header Value | `Basic <base64-encoded-login:password>` |

So generierst du den Base64-Wert (in Bash):
```bash
echo -n "<dein-login>:<dein-password>" | base64
```
Login + Password gibt's nach Account-Anmeldung unter dataforseo.com → My APIs.

### 6.3 GitHub PAT (Personal Access Token)

Fuer Memory-Bridge-Schreibzugriff auf das Memory-Repo:

1. github.com → Settings → Developer settings → Personal access tokens → **Tokens (classic)**
2. Generate new token (classic)
3. Scope: `repo` (Full control of private repositories)
4. Token kopieren — wird **nur einmal** angezeigt

In n8n als **HTTP Header Auth Credential**:
- Name: `GitHub Memory PAT`
- Header Name: `Authorization`
- Header Value: `Bearer <dein-pat>`

### 6.4 HTTP Bearer Auth (Master-Token fuer MCP-Trigger)

Dieses Token sichert alle MCP-Server-Endpoints. Gleicher Token fuer alle Workflows mit MCP-Trigger — vereinfacht Rotation.

1. **Token generieren** (z.B. mit `openssl rand -base64 48` oder einem Password-Manager)
2. In n8n: Credentials → Add → "Header Auth"
3. Name: `Google Ads Agent MCP Bearer`
4. Header Name: `Authorization`
5. Header Value: `Bearer <dein-master-token>`

### 6.5 Gmail OAuth2

Setup wie 6.1 (OAuth via Google Cloud), Scope: `https://www.googleapis.com/auth/gmail.send`.

Der OAuth-Account ist die Versand-Adresse fuer die Email.

### 6.6 LLM Provider — Anthropic ODER OpenAI

Die 6 AI-Agent-Workflows nutzen entweder Anthropic Claude oder OpenAI GPT. Die Workflows sind so eingerichtet, dass beide Optionen via "Mixed-Mode + Fallback-LLM" konfigurierbar sind (siehe `docs/learnings/n8n-ai-agent-v3-1-features.md`).

**Anthropic** (empfohlen fuer Reasoning-intensive Sub-Agenten wie Statistiker und Orchestrator):
| Feld | Wert |
|---|---|
| Type | Anthropic API |
| API Key | `sk-ant-...` |

**OpenAI** (gut fuer Composer und einfachere Sub-Agenten):
| Feld | Wert |
|---|---|
| Type | OpenAI API |
| API Key | `sk-...` |

Du kannst beide einrichten und in den Workflows zwischen primary und Fallback waehlen.

---

## 7. MCP-Tool-Workflows importieren

Die 9 MCP-Tool-Workflows liegen unter `workflows/mcp-tools/`. Reihenfolge: 01 → 09 (technisch egal, aber so behaeltst du Ordnung).

### 7.1 Pro Workflow

Fuer **jeden** der 9 Workflows:

1. **Import:** n8n-UI → Workflows → "Add Workflow" → ⋮-Menu → "Import from File" → JSON auswaehlen
2. **Customer-ID anpassen** (nur Workflows 01-08, nicht 09 DataForSEO):
   - Im Workflow per Suchen+Ersetzen (Strg+F): `<YOUR_CUSTOMER_ID>` → deine 10-stellige Customer-ID
   - `<YOUR_LOGIN_CUSTOMER_ID>` → deine Login-Customer-ID (MCC-ID); falls kein MCC: gleicher Wert wie Customer-ID
   - Diese stehen als Default-Werte in den HTTP-Request-Nodes (z.B. "list_campaigns", "get_campaign_performance")
3. **Credentials zuweisen:**
   - In ALLEN HTTP-Request-Nodes mit Google-Ads-URLs: Credential `Google Ads OAuth2` (aus 6.1) auswaehlen
   - In Workflow 09 (DataForSEO): Credential `DataForSEO HTTP Header Auth` (aus 6.2)
   - Im **MCP-Server-Trigger-Node** (oben links im Workflow): Authentication = "Bearer Auth", Credential = `Google Ads Agent MCP Bearer` (aus 6.4)
4. **Workflow speichern** (Save oben rechts)
5. **Workflow aktivieren** (Toggle "Active" oben rechts)
6. **Workflow-ID notieren** — du siehst sie in der URL (`/workflow/<ID>`) oder unter Settings → Workflow-ID. Notiere dir diese fuer Schritt 9.

### 7.2 Welche Workflow-ID fuer welchen Tool-Workflow

Trage die n8n-IDs in eine Tabelle ein. Du brauchst sie spaeter:

| # | Datei | Workflow-Name in n8n | n8n-Workflow-ID (eintragen) |
|---|---|---|---|
| 01 | `01-account-tools.json` | Google Ads MCP - Account Tools | `<deine-id>` |
| 02 | `02-campaign-tools.json` | Google Ads MCP - Campaign Tools | `<deine-id>` |
| 03 | `03-ad-group-tools.json` | Google Ads MCP - Ad Group Tools | `<deine-id>` |
| 04 | `04-ad-tools.json` | Google Ads MCP - Ad Tools | `<deine-id>` |
| 05 | `05-keyword-tools.json` | Google Ads MCP - Keyword Tools | `<deine-id>` |
| 06 | `06-reporting-tools.json` | Google Ads MCP - Reporting Tools | `<deine-id>` |
| 07 | `07-insights-tools.json` | Google Ads MCP - Insights Tools | `<deine-id>` |
| 08 | `08-gaql-tools.json` | Google Ads MCP - GAQL Tools | `<deine-id>` |
| 09 | `09-dataforseo-mcp.json` | DataForSEO_MCP_Server_v2 | `<deine-id>` |

---

## 8. Agent-Team-Workflows importieren

Die 8 Agent-Team-Workflows liegen unter `workflows/agent-team/`.

**Reihenfolge wichtig:**
1. Erst `11-github-memory-helper.json` (Sub-Workflow ohne Abhaengigkeiten)
2. Dann `10-memory-bridge.json` (ruft 11)
3. Dann die 5 Sub-Agenten: `12, 13, 15, 16, 17` (rufen MCP-Tools + Memory-Bridge)
4. Zuletzt `14-main-orchestrator.json` (ruft alle Sub-Agenten + Memory + Tools)

### 8.1 Pro Workflow

1. **Import** wie in 7.1
2. **Credentials zuweisen** (je nach Workflow):

| Workflow | Benoetigte Credentials |
|---|---|
| `11-github-memory-helper` | GitHub PAT (6.3) — in den HTTP-Request-Nodes mit `api.github.com` |
| `10-memory-bridge` | Bearer Auth (6.4) im MCP-Trigger; ruft Workflow 11 als Sub-Workflow |
| `12-sub-report-composer` | Anthropic ODER OpenAI (6.6) im AI-Agent-Node |
| `13-sub-market-intelligence` | Anthropic ODER OpenAI (6.6) |
| `15-sub-performance-analyst` | Anthropic ODER OpenAI (6.6) |
| `16-sub-search-keyword-analyst` | Anthropic ODER OpenAI (6.6) |
| `17-sub-statistician` | Anthropic ODER OpenAI (6.6) |
| `14-main-orchestrator` | Anthropic ODER OpenAI (6.6); Schedule-Trigger (kein Credential) |

3. **Anpassungen in `11-github-memory-helper`:**
   - Im Workflow: 3 HTTP-Request-Nodes haben URL `https://api.github.com/repos/<your-username>/google-ads-memory/contents/...`
   - **Ersetze `<your-username>` durch deinen GitHub-User**
4. **Workflow speichern** und **aktivieren**
5. **Workflow-ID notieren**:

| # | Datei | Workflow-Name in n8n | n8n-Workflow-ID (eintragen) |
|---|---|---|---|
| 10 | `10-memory-bridge.json` | Google Ads Memory Bridge | `<deine-id>` |
| 11 | `11-github-memory-helper.json` | GitHub Memory Helper (Auth Wrapper for Memory Bridge) | `<deine-id>` |
| 12 | `12-sub-report-composer.json` | GoogleAdsAgent - Sub: Report Composer | `<deine-id>` |
| 13 | `13-sub-market-intelligence.json` | GoogleAdsAgent - Sub: Market Intelligence | `<deine-id>` |
| 14 | `14-main-orchestrator.json` | GoogleAdsAgent - Main: Orchestrator (Chat + Weekly) | `<deine-id>` |
| 15 | `15-sub-performance-analyst.json` | GoogleAdsAgent - Sub: Performance Analyst | `<deine-id>` |
| 16 | `16-sub-search-keyword-analyst.json` | GoogleAdsAgent - Sub: Search & Keyword Analyst | `<deine-id>` |
| 17 | `17-sub-statistician.json` | GoogleAdsAgent - Sub: Statistician | `<deine-id>` |

---

## 9. Workflow-IDs zwischen Workflows verknuepfen

Hier die wichtigste — und am haeufigsten uebersehene — Setup-Aufgabe.

### 9.1 Was passiert?

Die Sub-Agenten und der Orchestrator rufen andere Workflows als **Sub-Workflows** auf. Die Workflow-IDs in den importierten JSON-Dateien sind die **alten n8n-IDs aus dem Quell-System** und zeigen NICHT auf deine n8n-Workflows. Du musst sie ersetzen.

Wenn du sie nicht ersetzt: Beim ersten Run des Orchestrators kommt der Fehler **"Workflow ID not found"**.

### 9.2 ID-Mapping-Tabelle

In den importierten Workflows tauchen diese Quell-IDs auf. Ersetze sie alle durch deine eigenen Workflow-IDs aus Schritt 7.2 + 8.1:

| Alte Quell-ID (in JSON) | Tool-Name im Agent | Zeigt auf | **Deine n8n-ID** |
|---|---|---|---|
| `kl42z9WLAGLZzlBW` | call_performance_analyst | Workflow 15 | `<deine-id-15>` |
| `PZa1iNwgtCvcNtIC` | call_search_keyword_analyst | Workflow 16 | `<deine-id-16>` |
| `rBIHMb14pdtLRGTj` | call_statistician | Workflow 17 | `<deine-id-17>` |
| `15f8AxGRmwcC1fIM` | call_market_intelligence | Workflow 13 | `<deine-id-13>` |
| `6aZgqH9uhcXIngH0` | call_report_composer | Workflow 12 | `<deine-id-12>` |
| `hFLZBFb48I09iFdJ` | read_memory_file / write_memory_file | Workflow 10 | `<deine-id-10>` |
| `_MscqooFbXWKSMGS_3Oul` | campaign_performance / Reporting-Tools | Workflow 06 | `<deine-id-06>` |
| `X9OeaCnNCTFZpxzI_xbyh` | execute_gaql / GAQL-Tools | Workflow 08 | `<deine-id-08>` |
| `iXM_bBcOy3-72NRCuheg0` | get_recommendations / Insights-Tools | Workflow 07 | `<deine-id-07>` |
| `UnoWhmmvuvnjP4E4` | serp_search / DataForSEO | Workflow 09 | `<deine-id-09>` |

### 9.3 Wo die IDs ersetzen?

In **diesen Workflows** kommen die IDs vor (Suchen+Ersetzen im Editor in n8n):

| Workflow | Welche Quell-IDs sind drin |
|---|---|
| **14-main-orchestrator** | Alle 8 oberen IDs (Sub-Agenten 12/13/15/16/17 + Memory 10 + Reporting 06 + GAQL 08) |
| **15-sub-performance-analyst** | `_MscqooFbXWKSMGS_3Oul` (06), `X9OeaCnNCTFZpxzI_xbyh` (08), `hFLZBFb48I09iFdJ` (10) |
| **16-sub-search-keyword-analyst** | `_MscqooFbXWKSMGS_3Oul` (06), `iXM_bBcOy3-72NRCuheg0` (07), `X9OeaCnNCTFZpxzI_xbyh` (08), `UnoWhmmvuvnjP4E4` (09), `hFLZBFb48I09iFdJ` (10) |
| **17-sub-statistician** | `_MscqooFbXWKSMGS_3Oul` (06), `iXM_bBcOy3-72NRCuheg0` (07), `X9OeaCnNCTFZpxzI_xbyh` (08), `hFLZBFb48I09iFdJ` (10) |
| **13-sub-market-intelligence** | `_MscqooFbXWKSMGS_3Oul` (06), `iXM_bBcOy3-72NRCuheg0` (07), `X9OeaCnNCTFZpxzI_xbyh` (08), `UnoWhmmvuvnjP4E4` (09), `hFLZBFb48I09iFdJ` (10) |
| **12-sub-report-composer** | `hFLZBFb48I09iFdJ` (10) |

### 9.4 Wie ersetzen?

**Variante A — UI-Klick-Methode (sicher, langsam):**
1. Workflow oeffnen in n8n
2. Auf jeden `Tool: Workflow`- oder `Execute Workflow`-Node klicken
3. Im Feld "Workflow" das Dropdown oeffnen → deine importierte n8n-ID auswaehlen
4. Workflow speichern
5. Wiederholen fuer alle Workflows aus 9.3

**Variante B — Direkt im JSON (schnell):**
1. Workflow aus n8n exportieren (Workflows-Liste → ⋮ → "Download")
2. Im Editor: Suchen+Ersetzen `kl42z9WLAGLZzlBW` → `<deine-id-15>` (etc. fuer alle 10 IDs)
3. Modifiziertes JSON wieder importieren (alten Workflow loeschen, neu hochladen)

Variante A ist robuster, weil Variante B leicht zu Inkonsistenz fuehrt (z.B. Cache-Felder im JSON die nicht aktualisiert werden).

---

## 10. Customer-IDs in den Tool-Workflows anpassen

Bereits erledigt in Schritt 7.1 falls du die Anweisung dort befolgt hast. Stell sicher dass:

- **In den 8 Google-Ads-Tool-Workflows (01-08):** in jedem HTTP-Request-Node mit Google-Ads-URL ist als Customer-ID **deine** ID eingetragen, nicht `<YOUR_CUSTOMER_ID>`
- **In Workflow 11 (GitHub-Memory-Helper):** alle 3 GitHub-API-URLs zeigen auf **dein** `<dein-user>/google-ads-memory`

Quick-Check via n8n:
```
Workflows-Liste → ⋮-Menu → "Search across workflows" → "<YOUR_CUSTOMER_ID>"
```
Sollte 0 Treffer zeigen.

---

## 11. Mail-Bridge anlegen (optional)

Der Report-Composer kann den Report per Email versenden. Im Repo ist der Mail-Bridge-Workflow nicht enthalten (weil Gmail-OAuth-spezifisch), aber er ist schnell selbst gebaut:

### 11.1 Neuer Workflow in n8n

1. **Workflows → Add Workflow → "Mail-Bridge"**
2. **Trigger:** "MCP Server Trigger"
   - Path: `mail-bridge`
   - Authentication: "Bearer Auth" → Credential `Google Ads Agent MCP Bearer` (6.4)
3. **Tool-Node:** "Gmail" → Operation: "Send"
   - Credential: `Gmail OAuth2` (6.5)
   - To: `={{ $json.to }}`
   - Subject: `={{ $json.subject }}`
   - Message: `={{ $json.body_html }}` (HTML enabled)
4. Speichern + aktivieren

### 11.2 Composer-Workflow anpassen

Im **Workflow 12 (Report-Composer)** im AI-Agent: Tool `send_email` per Sub-Workflow ergaenzen, das auf deinen Mail-Bridge-Workflow zeigt. Alternativ: Den `MCP Client`-Node nutzen, der ueber HTTP-Bearer auf `https://<your-n8n-host>/mcp/mail-bridge` zugreift.

Wenn du keine Email willst: ueberspringe diesen Schritt — Composer schreibt den Report trotzdem ins Memory-Repo.

---

## 12. Test-Run

### 12.1 Voraussetzungen-Check

Vor dem ersten Run:
- [ ] Alle 17 Workflows importiert + aktiviert + Workflow-IDs notiert
- [ ] Alle Workflow-ID-Refs aus Schritt 9 ersetzt
- [ ] Customer-IDs in 01-08 ersetzt
- [ ] Memory-Repo befuellt mit Strategy-Manifest
- [ ] Credentials in allen Nodes zugewiesen (Quick-Check: rote Punkte an Nodes = fehlende Credential)

### 12.2 Smoke-Test pro MCP-Workflow

Pro Tool-Workflow (z.B. 01-account-tools): Workflow oeffnen → "Execute workflow" → MCP-Trigger → Workflow durchlaufen lassen. Erwartet: Tools werden aufgelistet, Sample-Calls funktionieren ohne Auth-Fehler.

### 12.3 Smoke-Test des Memory-Helpers

Workflow 11 (GitHub-Memory-Helper) hat einen `executeWorkflowTrigger` — du kannst ihn manuell triggern mit Test-Input:
```json
{
  "tool_name": "read_memory_file",
  "filename": "00_strategy_manifest.md"
}
```
Erwartet: Datei-Inhalt aus deinem Memory-Repo wird zurueckgegeben.

### 12.4 Full-Run via Chat-Trigger

Der **Orchestrator (Workflow 14)** hat einen Chat-Trigger:

1. Workflow 14 in n8n oeffnen
2. Oben rechts: "Open chat" Button
3. Eingabe: `Run weekly report for current ISO week`
4. Erwartet:
   - Orchestrator liest Memory (read_memory_file × 2)
   - Orchestrator dispatcht 4 Sub-Agenten parallel
   - Jeder Sub-Agent ruft mehrere Tool-Workflows auf
   - Composer wird gerufen, rendert Report
   - Memory wird via Memory-Bridge geschrieben
   - Total ca. 8-15 min

### 12.5 Validation

1. **GitHub Memory-Repo:** sollte `reports/<aktuelle-iso-week>-report.md` enthalten (Contents inspizieren)
2. **`02_findings_log.md`:** sollte neue Eintraege haben
3. **`03_pending_actions.md`:** sollte aktuelle KW als neuer Block haben
4. **Email** (wenn 11 konfiguriert): kommt an mit Executive Summary

Wenn der Report leer in einer Sektion ist (z.B. Sektion 5 leer): siehe Troubleshooting.

---

## 13. Schedule aktivieren

Im Orchestrator (Workflow 14) gibt es zwei Trigger:
- **Chat-Trigger** — fuer manuelle Runs
- **Schedule-Trigger** — fuer wiederkehrende Runs

### 13.1 Schedule-Trigger konfigurieren

1. Workflow 14 oeffnen
2. Schedule-Trigger-Node anklicken
3. Mode: "Custom (Cron)" — Beispiel: `0 7 * * 1` (jeden Montag 07:00)
4. Timezone: `Europe/Berlin` (oder deine Wunsch-TZ)
5. Workflow speichern + Toggle "Active" pruefen

### 13.2 Cron-Test

Setze die Cron-Expression initial auf z.B. 10 Minuten in der Zukunft:
```
[Min] [Stunde] * * *
```
Beobachte ob der Orchestrator startet. Dann zurueck auf den eigentlichen Schedule.

---

## 14. Troubleshooting

| Symptom | Ursache | Loesung |
|---|---|---|
| `Workflow ID not found` beim Sub-Workflow-Call | Quell-ID nicht ersetzt | Schritt 9 wiederholen |
| `401 Unauthorized` auf Google Ads API | OAuth-Token abgelaufen / falscher Account | OAuth-Credential in n8n re-authorisieren; pruefen ob Account-Login Zugriff auf Customer-ID hat |
| `403 USER_PERMISSION_DENIED` | Login-Customer-ID falsch oder Account hat keinen API-Zugang | Login-Customer-ID = MCC-ID; Customer-ID muss MCC-Subkonto sein. Bei Single-Account: Login-Customer-ID = Customer-ID. Falls API-Zugang fehlt: Developer Token Tier erhoehen. |
| `429 Too Many Requests` Google Ads | Rate-Limit | Sub-Agenten haben "Hard Caps" (max Tool-Calls); pruefen ob jemand sie umgangen hat. Sonst Developer-Token-Tier erhoehen. |
| Sub-Agent gibt leeres JSON zurueck | LLM-Tokens zu klein / Streaming-Timeout | LLM-Modell pruefen (Anthropic Sonnet/Opus 4 minimum), maxIterations im AI-Agent-Node erhoehen |
| Composer-Report ist leer in Sektion X | Sub-Agent X hat `DATA_UNAVAILABLE` zurueckgegeben | Workflow-Execution X anschauen — welcher Tool-Call hat versagt? Meist Auth- oder Rate-Limit-Problem |
| Memory-Bridge Schreibfehler `409 Conflict` | Race-Condition bei parallelen Edits | Memory-Helper hat Atomic-Edit-Pattern eingebaut — sollte automatisch retryen. Bei wiederholtem Fehler: GitHub-PAT-Scope pruefen (`repo` voll noetig) |
| Memory-Helper `404 Not Found` | GitHub-User oder Repo-Name falsch | Workflow 11 anschauen → URLs auf `api.github.com/repos/<dein-user>/google-ads-memory/...` korrigieren |
| Statistiker liefert nur `insufficient_data` | Sample-Size zu klein | Bei sehr neuem Account: warten bis genug Daten. Bei laufendem Account: GAQL-Range-Adapter pruefen (sollte automatisch auf 14d/30d/90d erweitern) |
| Customer-IDs `<YOUR_CUSTOMER_ID>` werden nicht ersetzt | Workflows nicht angepasst nach Import | Schritt 7.1 / Schritt 10 wiederholen |
| Schedule feuert nicht | Workflow nicht aktiv | Toggle "Active" oben rechts pruefen |

### Debug-Workflow

1. **n8n-Executions-View** (Workflows → Executions): jeder Run wird hier geloggt mit Step-fuer-Step JSON-Outputs
2. **Pro Sub-Agent:** AI-Agent-Node anklicken → "View output" → "Logs" zeigt LLM-Calls + Tool-Calls
3. **Pro Tool-Call:** Sub-Workflow-Execution oeffnen, sehen welche Inputs/Outputs

---

## 15. FAQ

**F: Brauche ich alle 17 Workflows?**
A: Ja, es ist ein integriertes System. Wenn du z.B. den Statistiker raus laesst, faellt Sektion 8 im Report leer aus. Wenn du Memory-Bridge raus laesst, kann nichts ins Memory-Repo geschrieben werden.

**F: Kann ich Anthropic UND OpenAI parallel nutzen?**
A: Ja — die AI-Agent-Workflows v3.1 unterstuetzen "Mixed-Mode + Fallback-LLM". Du kannst z.B. Anthropic primary + OpenAI fallback einrichten. Siehe `docs/learnings/n8n-ai-agent-v3-1-features.md`.

**F: Wie aendere ich die Sub-Agent-Prompts?**
A: Pro Sub-Agent-Workflow (12, 13, 15, 16, 17) ist der Prompt im **AI Agent Node** im Feld "System Message" hinterlegt. Workflow oeffnen → AI Agent Node → "System Message" aendern. Speichern.

**F: Wie passe ich das Report-Template an?**
A: Im **Workflow 12 (Report-Composer)** ist das Template als System-Message des AI Agent Nodes hinterlegt. Direkt dort editieren.

**F: Kann ich mehrere Google-Ads-Accounts parallel reporten?**
A: Aktuell nicht ohne Workflow-Duplizierung. Customer-ID ist hardcoded in den Tool-Workflows. Multi-Tenant-Setup ist als Erweiterung moeglich (Customer-ID als Workflow-Variable + Routing).

**F: Wie deaktiviere ich Search-Term-Mining (Workflow 16)?**
A: Im Orchestrator (Workflow 14): den Tool-Node `call_search_keyword_analyst` deaktivieren oder loeschen. Dann wird der Sub-Agent nicht aufgerufen, Sektion 6 im Report bleibt leer.

**F: Wo sehe ich die Kosten der LLM-Calls?**
A: Auf der Anthropic/OpenAI-Konsole. n8n trackt die Kosten nicht. Pro Run typisch 30-50k Token = ~3-5 USD.

**F: Was, wenn ich keine MCP-Server (extern erreichbar) brauche?**
A: Kein Problem — die Workflows nutzen MCP-Trigger nur fuer optionale externe Anbindung. Intern laufen alle Calls ueber n8n-Sub-Workflows. Du kannst die MCP-Trigger sogar deaktivieren wenn du nur intern arbeitest.

---

## Verwandte Dokumente

- [README.md](../README.md) — Projekt-Uebersicht
- [docs/LEARNINGS.md](LEARNINGS.md) — Index dokumentierter Erkenntnisse zu n8n / Google Ads / DataForSEO
- [templates/memory/README.md](../templates/memory/README.md) — Memory-Repo-Struktur

---

*Bei Problemen: Issue im Repo oeffnen oder den Maintainer ansprechen.*
