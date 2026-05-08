# google-ads-agent

n8n-basiertes Multi-Agent-System fuer woechentliches Google-Ads-Reporting. Komplett in **n8n** implementiert — keine externen Orchestrierungs-Tools noetig.

Das Repo enthaelt:
- **9 MCP-Tool-Workflows** — Google Ads + DataForSEO API-Wrapper
- **8 Agenten-Team-Workflows** — Orchestrator + 4 Sub-Agenten (Performance, Search/KW, Statistiker, Market) + Composer + 2 Memory-Helper
- **Memory-Templates** — Strategy-Manifest + Findings-Log + Pending-Actions fuer eigenes Memory-Repo

## Was das System macht

Der **Orchestrator** (Workflow `14-main-orchestrator`) wird per Schedule (z.B. Mo 07:00) oder per Chat manuell getriggert. Er:

1. Liest Memory aus GitHub (Strategy, offene Hypothesen, P0/P1-Items)
2. Dispatcht 4 Sub-Agenten als n8n-Sub-Workflows:
   - **Performance-Analyst** — strukturelle KPIs (Spend/Conv/CPA, Campaign/Ad/Device/Geo/Hourly)
   - **Search & Keyword-Hunter** — Search-Terms-Mining, Negatives, Keyword-Opportunities (DataForSEO)
   - **Statistiker** — Hypothesen-Validierung mit Z-Test, Welch-t-Test, Cochran-Armitage
   - **Market & Competitive** — Auction Insights, Keyword-Trends, neue Wettbewerber
3. Uebergibt die 4 JSON-Outputs an den **Report-Composer**
4. Composer rendert 12-Sektionen-Markdown-Report
5. Memory-Bridge committet Report + aktualisiert Findings-Log/Pending-Actions im Memory-Repo
6. Versendet Executive-Summary per Email (via Gmail-Node)

## Repo-Struktur

```
google-ads-agent/
├── workflows/
│   ├── mcp-tools/         # 9 MCP-Server-Workflows (Google Ads + DataForSEO)
│   │   ├── 01-account-tools.json
│   │   ├── 02-campaign-tools.json
│   │   ├── 03-ad-group-tools.json
│   │   ├── 04-ad-tools.json
│   │   ├── 05-keyword-tools.json
│   │   ├── 06-reporting-tools.json
│   │   ├── 07-insights-tools.json
│   │   ├── 08-gaql-tools.json
│   │   └── 09-dataforseo-mcp.json
│   └── agent-team/        # 8 AI-Agenten + Helper-Workflows
│       ├── 10-memory-bridge.json          # MCP-Server: Memory-Schreibzugriffe
│       ├── 11-github-memory-helper.json   # Sub-Workflow: Atomic GitHub-Edits
│       ├── 12-sub-report-composer.json    # AI Agent: Report-Komposition
│       ├── 13-sub-market-intelligence.json # AI Agent: Market & Competitive
│       ├── 14-main-orchestrator.json      # AI Agent: Lead (Chat + Schedule)
│       ├── 15-sub-performance-analyst.json # AI Agent: Performance KPIs
│       ├── 16-sub-search-keyword-analyst.json # AI Agent: Search/Keywords
│       └── 17-sub-statistician.json       # AI Agent: Statistik
├── templates/
│   └── memory/            # Templates fuer eigenes Memory-Repo
│       ├── 00_strategy_manifest.md
│       ├── 02_findings_log.md
│       ├── 03_pending_actions.md
│       ├── README.md
│       └── reports/.gitkeep
├── docs/
│   ├── SETUP.md           # Schritt-fuer-Schritt Installations-Anleitung
│   ├── LEARNINGS.md       # Index dokumentierter Erkenntnisse
│   └── learnings/         # n8n + Google Ads + DataForSEO Learnings
├── memory/                # Submodule auf eigenes Memory-Repo
├── .env.example           # Optional: n8n API-Variablen fuer CLI-Tools
└── .gitignore
```

## Quick Start

Du brauchst eine eigene n8n-Instanz (≥ v1.104.0), einen Google Ads Account mit API-Zugang, einen DataForSEO Account, ein GitHub Repo fuer das Memory, und einen LLM-Provider (Anthropic oder OpenAI).

**Komplette Setup-Anleitung:** [docs/SETUP.md](docs/SETUP.md) (~30 min Lesezeit, 2-4h Setup-Zeit)

Kurzform:
1. Repo klonen
2. Eigenes Memory-Repo aufsetzen (`templates/memory/` als Vorlage)
3. n8n-Credentials anlegen (Google Ads OAuth, DataForSEO, GitHub PAT, Bearer-Auth, Gmail OAuth, LLM API Key)
4. 17 Workflows in n8n importieren (mcp-tools/ zuerst, dann agent-team/)
5. Customer-IDs + Workflow-IDs in den importierten Workflows anpassen
6. Orchestrator manuell testen via Chat-Trigger
7. Schedule-Trigger aktivieren

## Voraussetzungen

| Komponente | Wofuer |
|---|---|
| **n8n self-hosted ≥ v1.104.0** | MCP-Server-Trigger via Streamable HTTP, AI-Agent-Workflows v3.1 |
| **Google Cloud Project + OAuth-Client** | Google Ads API-Zugriff |
| **Google Ads Developer Token** | API-Zugang (Test- oder Production-Tier) |
| **DataForSEO Account (API)** | Keyword-Volumen, SERP, Competitor-Daten — Pay-as-you-go |
| **GitHub Repo + Personal Access Token** | Memory-Repo (Strategy, Findings, Reports) |
| **Anthropic / OpenAI API Key** | LLM-Calls in den AI-Agent-Workflows |
| **Gmail-Account + OAuth-Setup** | Email-Versand der Executive Summary |

## Lizenz / Verwendung

Dieses Setup ist als Template gedacht — du nutzt es fuer einen eigenen Google-Ads-Account, befuellst dein eigenes Memory-Repo, und betreibst die Workflows in deiner eigenen n8n-Instanz. Es findet keine Datenuebertragung an Dritte statt (ausser an die Drittanbieter-APIs: Google Ads, DataForSEO, dein LLM-Provider, GitHub).
