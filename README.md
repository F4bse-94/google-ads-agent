# google-ads-agent

Multi-Agent-System fuer woechentliches Google-Ads-Reporting nach Anthropic's Orchestrator-Worker-Pattern. Kein Chat-Bot, sondern eine **scheduled Pipeline**: jeden Montag morgen analysieren 4 spezialisierte AI-Agents parallel ein Google-Ads-Konto, ein Report-Composer rendert das Ergebnis als 12-Sektionen-Markdown, der Report wird ins Memory-Repo committet und per Email versendet.

> **Status:** Production-ready. Lokale Test-Runs in KW16-19/2026 durchgelaufen. Cloud-Routine-Deploy steht aus. **Read-only:** keine Write-Operationen auf Google-Ads-Konten.

---

## Was das System macht

Jeden Montag 07:00 Europe/Berlin (oder beliebiges anderes Cron-Schedule) laeuft eine Claude Code Routine in der Anthropic-Cloud, die:

1. **Memory-Repo klont** (`google-ads-memory` als Submodule) — Strategy-Manifest, offene Hypothesen, P0/P1-Items
2. **Orchestrator** (Opus 4.7) liest Memory, plant Reporting-Umfang
3. **4 Sub-Agents parallel:**
   - **Performance-Analyst** (Sonnet) — strukturelle KPIs (Spend/Conv/CPA, Campaign/Ad/Device/Geo/Hourly)
   - **Search & Keyword-Hunter** (Sonnet) — Search-Terms-Mining, Negatives-Kandidaten, Keyword-Opportunities via DataForSEO
   - **Statistiker** (Opus, eigener MCP-Zugriff) — Hypothesen-Validierung, Z-Tests/Welch-t/Cochran-Armitage, Re-Validation offener Items aus Vorwochen
   - **Market & Competitive** (Sonnet) — DataForSEO Auction Insights, Keyword-Trends, neue Wettbewerber
4. **Report-Composer** (Sonnet) rendert 12-Sektionen-Template
5. **Memory-Bridge** (n8n-Workflow) committet Report + aktualisiert findings_log/pending_actions im Memory-Repo
6. **Mail-Bridge** sendet Executive-Summary per Gmail

## Architektur

```
                         Claude Code Routine (Cloud)
                         ──────────────────────────
                                    │
                                    ▼
                ┌──────────────────────────────────────┐
                │  Orchestrator (Opus 4.7)             │
                │  liest Memory, dispatcht parallel    │
                └─┬────────┬────────┬────────┬─────────┘
                  │        │        │        │
       ┌──────────┘        │        │        └──────────┐
       ▼                   ▼        ▼                   ▼
 ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │Performance- │ │Search & KW-  │ │Statistiker   │ │Market &      │
 │Analyst      │ │Hunter        │ │(Opus)        │ │Competitive   │
 │(Sonnet)     │ │(Sonnet)      │ │              │ │(Sonnet)      │
 └──────┬──────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
        │               │                │                │
     n8n MCP         n8n MCP          n8n MCP          DataForSEO
    (Account,       (SearchTerms,    (GAQL,            MCP
     Reporting,     Keyword,          Reporting,
     Insights)      DataForSEO)       Insights)
        │               │                │                │
        └───────────────┴────────────────┴────────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  Report-Composer       │
                    │  (Sonnet)              │
                    │  12-Sektionen-Template │
                    └─┬───────────────────┬──┘
                      │                   │
                      ▼                   ▼
              ┌────────────────┐  ┌────────────────┐
              │ Memory-Bridge  │  │ Mail-Bridge    │
              │ (n8n)          │  │ (n8n)          │
              │ Report + Logs  │  │ Gmail          │
              │ → google-ads-  │  │ Executive      │
              │   memory       │  │ Summary        │
              └────────────────┘  └────────────────┘
```

Details: [docs/architecture.md](docs/architecture.md)

---

## Repo-Struktur

| Pfad | Inhalt |
|---|---|
| `.claude/agents/` | 7 Sub-Agent-Definitionen (Markdown + YAML-Frontmatter, dispatched via Task-Tool) |
| `.claude/rules/` | Globale Konventionen (n8n, Git, Documentation) |
| `skills/weekly-report/` | Skill mit Progressive Disclosure: SKILL.md + template.md + dispatch-playbook.md + references/ |
| `workflows/` | 17 n8n-Workflow-Backups (8 Google-Ads-MCPs + 1 DataForSEO-MCP + 2 Helper + 6 AI-Agent-Workflows) |
| `routines/` | Claude Code Routine Configs (Prompt + Cron + Connectors) |
| `memory/` | Git-Submodule auf `google-ads-memory` (Strategy, Findings, Pending-Actions, Reports) |
| `templates/memory/` | Memory-Templates fuer neuen Account (kopieren in eigenes Memory-Repo) |
| `docs/` | Architecture, Workflow-Atlas, Handoff-Contracts, Report-Anatomy, Learnings |
| `scripts/` | Python-Helpers fuer Statistik-Tests (Referenz-Implementation) |

---

## Quick Start

**Du bist neu?** Lies zuerst die ausfuehrliche Installations-Anleitung: [docs/SETUP.md](docs/SETUP.md)

Sehr verkuerzt:

```bash
# 1. Clone (mit Submodule)
git clone --recurse-submodules https://github.com/<user>/google-ads-agent.git
cd google-ads-agent

# 2. Eigenes Memory-Repo aufsetzen — Templates kopieren
# (Details in docs/SETUP.md, Schritt 4)

# 3. .env und .mcp.json aus Templates anlegen
cp .env.example .env             # Credentials eintragen
cp .mcp.json.example .mcp.json   # MCP-URLs + Bearer-Tokens

# 4. n8n-Workflows importieren (17 Stueck) — siehe SETUP.md, Schritt 5
# 5. Ersten lokalen Test-Run
claude
> Run the weekly-report skill for the current ISO week.

# 6. Cloud-Routine konfigurieren — siehe SETUP.md, Schritt 7
```

---

## Stack-Voraussetzungen

| Komponente | Version | Zweck |
|---|---|---|
| **n8n** (self-hosted) | ≥ v1.104.0 | MCP-Server-Trigger via Streamable HTTP, AI-Agent-Workflows |
| **Claude Code** | aktuell (CLI) | lokale Werkstatt + Cloud-Routine-Trigger |
| **Anthropic Plan** | Pro / Max / Team / Enterprise | Claude Code Routines (Cloud-Scheduling) |
| **Google Ads API** | v20+ | via n8n OAuth in Workflow-Credentials |
| **DataForSEO** | API v3 | Keyword-Volumen, SERP, Competitor-Daten |
| **GitHub PAT** | classic, `repo`-Scope | Memory-Repo Read+Write |
| **Gmail-Connector** | claude.ai Workspace | Email-Versand der Executive Summary |

---

## Read-Only Phase

Aktuell sind **alle Write-Operationen auf Google Ads deaktiviert**. Tools (`create_*`, `update_*`, `pause_*`, `remove_*`) sind in den n8n-Workflows zwar verfuegbar, werden aber von keinem Sub-Agent angerufen. Sub-Agent-Prompts enthalten harte Boundaries (`READ_ONLY: true`).

Phase-2-Roadmap (Write-Operationen mit Approval-Gate): siehe [DECISIONS.md](DECISIONS.md).

---

## Originalauftrag

Ueberfuehrung eines Langdock-basierten Multi-Agent-Reportings (4 Agents in einem manuellen Chat-Flow) in eine vollautonom scheduled Cloud-Pipeline mit:
- 90% Performance-Gain durch Anthropic's Orchestrator-Worker-Pattern (gemaess Anthropic Multi-Agent Research)
- Memory-Repo als Single-Source-of-Truth zwischen Sessions
- n8n als deterministisches Tool-Backend (kein AI-Reasoning in n8n)
- Read-only-Phase fuer Vertrauensaufbau, dann Write-Operations mit Approval-Gate
