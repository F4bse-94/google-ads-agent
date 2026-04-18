# google-ads-agent

Multi-Agent-System zur wochentlichen Analyse des MVV Enamic Ads Google-Ads-Kontos (CID `2011391652`). Nachfolger des Langdock-Systems, neu konzipiert nach Anthropic's Orchestrator-Worker-Pattern mit Claude Code Routines als Cloud-Scheduling-Layer.

**Status (2026-04-17):** Phase 1 (Scaffolding) aktiv. MVP-Ziel: Weekly Read-Only Report per Email.

---

## Was macht das System

Jeden Montag 07:00 Europe/Berlin laeuft automatisch eine Claude Code Routine in der Anthropic-Cloud, die:

1. Das Memory-Repo (`google-ads-memory`) klont — Strategie, offene Follow-ups, Top-Performer, Negatives
2. **Orchestrator** (Opus 4.7) liest Memory, plant Reporting-Umfang
3. **4 parallele Sub-Agents** ziehen Daten und analysieren:
   - Performance-Analyst — strukturelle KPIs (Spend/Conv/CPA, Campaign/Ad/Device/Geo)
   - Search & Keyword-Hunter — Search-Terms-Mining, Negatives-Kandidaten, Keyword-Opportunities
   - Statistiker (Opus 4.7, eigener MCP-Zugriff) — Signifikanz-Validierung, Trend-Tests
   - Market & Competitive — DataForSEO Auction Insights, Keyword-Trends, neue Wettbewerber
4. **Report-Composer** rendert strukturiertes 12-Sektionen-Template
5. Schreibt Markdown-Report in `google-ads-memory/reports/YYYY-WNN.md`
6. Sendet Email via Gmail-Connector an Fabian (weiterleitbar an Agentur)

## Architektur-Diagramm

```
                        Claude Code Routine (Cloud)
                        ──────────────────────────
                                   │
                                   ▼
              ┌──────────────────────────────────────┐
              │  Orchestrator (Opus 4.7)             │
              │  liest Memory, dispatcht parallel    │
              └──┬──────┬──────┬──────┬──────────────┘
                 │      │      │      │
         ┌───────┘      │      │      └───────┐
         ▼              ▼      ▼              ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │Performance│ │Search &  │ │Statistiker│ │Market &  │
    │Analyst    │ │KW-Hunter │ │(Opus)     │ │Competit. │
    │(Sonnet)   │ │(Sonnet)  │ │           │ │(Sonnet)  │
    └─────┬─────┘ └─────┬────┘ └─────┬─────┘ └─────┬────┘
          │             │            │             │
       n8n MCPs     n8n MCPs      n8n MCPs     DataForSEO
       (Account,    (Keyword,     (GAQL,       MCP (neu)
        Reporting,  Reporting-   Reporting)
        Insights)   SearchTerms,
                    DataForSEO)
          │             │            │             │
          └─────────────┴────────────┴─────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │  Report-Composer       │
                  │  (Sonnet 4.6)          │
                  │  12-Sektionen-Template │
                  └───┬───────────────┬────┘
                      │               │
                      ▼               ▼
                ┌──────────┐    ┌──────────┐
                │ GitHub   │    │ Gmail    │
                │ Commit   │    │ Email    │
                │ (report) │    │ (Fabian) │
                └──────────┘    └──────────┘
                      │
                      ▼
              ┌──────────────────┐
              │ Memory-Writer    │
              │ (Tool, determ.)  │
              │ Session-Log,     │
              │ Findings-Log,    │
              │ Negatives update │
              └──────────────────┘
```

Details: [docs/architecture.md](docs/architecture.md)

---

## Ordner-Struktur

| Pfad | Inhalt |
|---|---|
| `.claude/agents/` | Sub-Agent-Definitionen (Claude Code Markdown mit YAML-Frontmatter) |
| `agents/` | Portable Systemprompts (auch in Langdock/n8n reuseable) |
| `skills/` | Filesystem-Skills mit Progressive Disclosure (SKILL.md + references/) |
| `memory/` | Git-Submodule `google-ads-memory` — Strategy, Session-Log, Findings, Negatives, Top-Performers, Report-Historie |
| `workflows/` | n8n JSON-Backups (8 Google-Ads-MCPs + 1 DataForSEO-MCP, Ground Truth) |
| `routines/` | Claude Code Routine Configs (Prompt, Cron, Connectors) |
| `docs/` | Architektur, Workflow-Atlas, Handoff-Contracts, Report-Anatomy, Learnings |
| `input/` | Ad-hoc CSVs, manuelle Daten |

## Abhaengigkeiten

**n8n-MCPs (self-hosted, `srv867988.hstgr.cloud`, Voraussetzung: n8n ≥ v1.104.0 fuer Streamable HTTP):**
- Account Tools — `LfP_dBhBCFuNOZmmiKAqH`
- Campaign Tools — `bJoXdsVd4k0wLX_3w8llU`
- Ad Group Tools — `aR0whx3Ak9pTKIYFgSab2`
- Ad Tools — `_Dnf-_VzFksABXNp6paro`
- Keyword Tools — `ewcJmnwFAJgJPjTV7d587`
- Reporting Tools — `_MscqooFbXWKSMGS_3Oul`
- Insights Tools — `iXM_bBcOy3-72NRCuheg0`
- GAQL Tools — `X9OeaCnNCTFZpxzI_xbyh`
- **DataForSEO Tools** — wird in Phase 2 neu gebaut

**Anthropic-Services:**
- Claude Code Routines (Pro/Max/Team/Enterprise) fuer Cloud-Scheduling
- Gmail-Connector fuer Email-Versand
- GitHub-Connector fuer Memory-Reads/Writes

**Externe APIs:**
- Google Ads API (via n8n OAuth, Customer-ID `2011391652`, Login-Customer-ID `5662771991`)
- DataForSEO (Phase 2 — API-Key noch einzurichten)

## Quick Start (fuer spaeter, sobald MVP laeuft)

```bash
# Lokale Prototypen-Session (Claude Code):
cd google-ads-agent
claude  # nutzt .mcp.json mit 9 MCP-Servern + GitHub + Gmail

# Manuell Weekly Report triggern:
> Run the weekly-report skill for ISO week 17 of 2026.

# Cloud-Routine triggern (nach Phase 6):
# via claude.ai/code/routines -> "Weekly Google Ads Report" -> Run now
```

## Aktueller MVP-Fortschritt

- [x] Plan approved (`C:\Users\fabia\.claude\plans\so-ich-m-chte-jetzt-lazy-noodle.md`)
- [ ] Phase 1: Scaffolding & Docs (in Arbeit)
- [ ] Phase 2: Workflow-Backups & DataForSEO-MCP + n8n Version-Check
- [ ] Phase 3: Memory-Repo Setup
- [ ] Phase 4: Prompts & Skills
- [ ] Phase 5: Lokaler Routine-Test
- [ ] Phase 6: Cloud-Deploy
- [ ] Phase 7: Monitoring & Iteration

## Initial erstellt

2026-04-17
