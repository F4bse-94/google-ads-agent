# Workflow Atlas — MCP-Server-Uebersicht

Dokumentation der 8 bestehenden n8n Google-Ads-MCP-Server + 1 geplanter DataForSEO-MCP. Quelle: live n8n-Instanz `srv867988.hstgr.cloud`. Alle folgen dem Hub-and-Spoke-Pattern (MCP Trigger → Tool-Workflows → Switch → HTTP Request → Format Code).

**Basis-Config aller Google-Ads-MCPs:**
- `loginCustomerId: 5662771991` (hardcoded in Set-Credentials-Nodes)
- `customerId: 2011391652` (MVV Enamic Ads)
- OAuth: Google Ads API via n8n-Credentials

---

## 1. Google Ads MCP — Account Tools

**Workflow-ID:** `LfP_dBhBCFuNOZmmiKAqH`
**Node-Count:** 13 | **Tools:** 3

### Tools
| Tool | Input | Output |
|---|---|---|
| `list_accessible_customers` | — | Liste aller zugaenglichen Customer-IDs |
| `get_account_hierarchy` | customerId | Tree mit Parent/Child-Beziehungen |
| `get_account_info` | customerId | Name, Currency, Timezone, Status |

### Typische Nutzung
- Bootstrap einer Analyse-Session (welche Accounts habe ich?)
- Validation dass Customer-ID aktiv und zugreifbar

### Nutzt welcher Agent
Performance-Analyst (selten, nur Session-Start-Check)

---

## 2. Google Ads MCP — Campaign Tools

**Workflow-ID:** `bJoXdsVd4k0wLX_3w8llU`
**Node-Count:** 20 | **Tools:** 7 (4 Read + 3 Write + 1 CRUD-Read)

### Tools
| Tool | Typ | Zweck |
|---|---|---|
| `list_campaigns` | READ | Alle Kampagnen mit Status, Budget, Bid-Strategy |
| `get_campaign` | READ | Details zu einer Kampagne |
| `create_campaign` | **WRITE** ⚠️ | Neue Kampagne anlegen — **NICHT IN MVP NUTZEN** |
| `update_campaign` | **WRITE** ⚠️ | Budget/Bidding/Name aendern — **NICHT IN MVP** |
| `pause_campaign` | **WRITE** ⚠️ | Pausieren — **NICHT IN MVP** |
| `enable_campaign` | **WRITE** ⚠️ | Aktivieren — **NICHT IN MVP** |
| `remove_campaign` | **WRITE** ⚠️ | Loeschen — **NICHT IN MVP** |

### Typische Nutzung
- Performance-Analyst: `list_campaigns` fuer Struktur-Overview

### Nutzt welcher Agent
Performance-Analyst (nur READ-Tools)

---

## 3. Google Ads MCP — Ad Group Tools

**Workflow-ID:** `aR0whx3Ak9pTKIYFgSab2`
**Node-Count:** 20 | **Tools:** 7 (analog zu Campaign Tools)

### Tools
| Tool | Typ | Zweck |
|---|---|---|
| `list_ad_groups` | READ | Alle Ad Groups einer Kampagne |
| `get_ad_group` | READ | Details zu einer Ad Group |
| `create_ad_group` | **WRITE** ⚠️ | — |
| `update_ad_group` | **WRITE** ⚠️ | — |
| `pause_ad_group` | **WRITE** ⚠️ | — |
| `enable_ad_group` | **WRITE** ⚠️ | — |
| `remove_ad_group` | **WRITE** ⚠️ | — |

### Nutzt welcher Agent
Performance-Analyst (READ), spaeter Post-MVP auch Write

---

## 4. Google Ads MCP — Ad Tools

**Workflow-ID:** `_Dnf-_VzFksABXNp6paro`
**Node-Count:** 20 | **Tools:** 7

### Tools
| Tool | Typ | Zweck |
|---|---|---|
| `list_ads` | READ | Alle Ads einer Ad Group mit Status, Ad-Strength |
| `get_ad` | READ | Details zu einem Ad (Headlines, Descriptions, URLs, Strength) |
| `create_responsive_search_ad` | **WRITE** ⚠️ | Neue RSA anlegen — Post-MVP |
| `update_ad` | **WRITE** ⚠️ | — |
| `pause_ad` | **WRITE** ⚠️ | — |
| `enable_ad` | **WRITE** ⚠️ | — |
| `remove_ad` | **WRITE** ⚠️ | — |

### Nutzt welcher Agent
Search & Keyword-Hunter (Ad-Copy-Audit), Performance-Analyst (Ad-Perf-Overview)

---

## 5. Google Ads MCP — Keyword Tools

**Workflow-ID:** `ewcJmnwFAJgJPjTV7d587`
**Node-Count:** 20 | **Tools:** 7

### Tools
| Tool | Typ | Zweck |
|---|---|---|
| `list_keywords` | READ | Keywords einer Ad Group mit Status, Bid, Match-Type |
| `get_keyword` | READ | Details zu einem Keyword |
| `add_keyword` | **WRITE** ⚠️ | — |
| `update_keyword_bid` | **WRITE** ⚠️ | — |
| `pause_keyword` | **WRITE** ⚠️ | — |
| `enable_keyword` | **WRITE** ⚠️ | — |
| `remove_keyword` | **WRITE** ⚠️ | — |

### Nutzt welcher Agent
Search & Keyword-Hunter (READ)

---

## 6. Google Ads MCP — Reporting Tools

**Workflow-ID:** `_MscqooFbXWKSMGS_3Oul`
**Node-Count:** 21 | **Tools:** 8 (alle READ)

### Tools
| Tool | Parameter | Output |
|---|---|---|
| `campaign_performance` | date_range, metrics | Pro Kampagne: Impressions, Clicks, Cost, Conv, CPA, CTR |
| `keyword_performance` | date_range | Pro Keyword: KPIs, QS, IS |
| `ad_performance` | date_range | Pro Ad: KPIs, Ad-Strength |
| `search_terms_report` | date_range | Actual search queries, impressions, clicks, conv |
| `budget_pacing` | — | Aktueller Spend vs. Budget, Forecast |
| `geographic_performance` | date_range | Breakdown nach Region/Country |
| `device_performance` | date_range | Mobile/Desktop/Tablet Breakdown |
| `hourly_performance` | date_range | 24-Stunden-Breakdown |

### Typische Zeitfenster
- `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `LAST_90_DAYS`, `THIS_MONTH`, `LAST_MONTH`

### Nutzt welcher Agent
Performance-Analyst (primaer), Statistiker (Rohdaten-Pulls), Search & KW-Hunter (search_terms_report)

---

## 7. Google Ads MCP — Insights Tools

**Workflow-ID:** `iXM_bBcOy3-72NRCuheg0`
**Node-Count:** 22 | **Tools:** 8 (6 READ + 2 Write)

### Tools
| Tool | Typ | Zweck |
|---|---|---|
| `top_campaigns_by_cost` | READ | Ranking nach Spend |
| `top_campaigns_by_conversions` | READ | Ranking nach Conv |
| `underperforming_keywords` | READ | Money Burners (High Cost, 0 Conv) |
| `conversion_trends` | READ | Conv-Entwicklung ueber Zeit |
| `anomaly_detection` | READ | Auto-flagged Anomalien (Wochentag-korrigiert) |
| `get_recommendations` | READ | Google-eigene Recs |
| `apply_recommendation` | **WRITE** ⚠️ | Rec uebernehmen — Post-MVP |
| `dismiss_recommendation` | **WRITE** ⚠️ | Rec ablehnen — Post-MVP |

### Nutzt welcher Agent
Performance-Analyst (Top-N-Listen, Anomalien), Market & Competitive (Recs), Search & KW-Hunter (underperforming_keywords)

---

## 8. Google Ads MCP — GAQL Tools

**Workflow-ID:** `X9OeaCnNCTFZpxzI_xbyh`
**Node-Count:** 10 | **Tools:** 2

### Tools
| Tool | Parameter | Output |
|---|---|---|
| `execute_gaql` | query (GAQL-String) | Raw Query Results |
| `search_stream` | query | Streamed Results fuer grosse Datenmengen |

### Typische Nutzung
- Statistiker: benutzerdefinierte Abfragen, die die Reporting-Tools nicht abdecken
- z.B. Auction Insights (`auction_insight_domain`), Quality-Score-Components, Conversion-Lag-Analysen

### GAQL-Beispiele

```sql
-- Impression Share Split
SELECT campaign.name, metrics.search_impression_share,
       metrics.search_budget_lost_impression_share,
       metrics.search_rank_lost_impression_share
FROM campaign
WHERE segments.date DURING LAST_7_DAYS

-- Quality Score Components
SELECT keyword_view.resource_name, ad_group_criterion.quality_info.quality_score,
       ad_group_criterion.quality_info.creative_quality_score,
       ad_group_criterion.quality_info.post_click_quality_score,
       ad_group_criterion.quality_info.search_predicted_ctr
FROM keyword_view
WHERE segments.date DURING LAST_7_DAYS

-- Conversion Lag
SELECT segments.conversion_lag_bucket, metrics.all_conversions
FROM campaign
WHERE segments.date DURING LAST_90_DAYS
```

### Nutzt welcher Agent
Statistiker (primaer), Performance-Analyst (Auction Insights)

---

## 9. DataForSEO MCP — `DataForSEO_MCP_Server_v2`

**Workflow-ID:** `UnoWhmmvuvnjP4E4`
**Node-Count:** 21 | **Tools:** 8 (alle READ) | **Status:** Live in n8n
**Hub-and-Spoke-Pattern:** gleiche Topologie wie die 8 Google-Ads-MCPs.

### Tools (live, verified 2026-04-17)
| Tool | Zweck |
|---|---|
| `serp_search` | Aktuelle SERP fuer eine Query (inkl. organische Treffer + Ads) |
| `keyword_overview` | Search Volume, CPC, Competition fuer 1-N Keywords |
| `keyword_suggestions` | Verwandte Keywords zu einem Seed |
| `domain_overview` | KW-Count, Traffic-Estimate, Top-KWs einer Domain |
| `search_volume` | Historische Volume-Entwicklung (Monats-Granularitaet) |
| `ranked_keywords` | Welche KWs rankt eine Domain gerade (organisch + paid) |
| `competitors_domain` | Domains die fuer Seed-Keywords ranken (Competitive Scan) |
| `related_keywords` | Semantic Cluster zu einem Seed |

### API-Basis
- Endpoint: `api.dataforseo.com`
- Auth: Basic Auth (Login + Password via n8n-Credentials)
- Quota-Kontrolle: Credits-basiert, ~50-100 USD/Monat fuer unseren Scope

### Nutzt welcher Agent
- **Market & Competitive** (primaer) — Auction-Flanke, Competitor-Tracking, Volume-Trends
- **Search & Keyword-Hunter** (sekundaer) — `keyword_suggestions` + `related_keywords` fuer Expansion-Kandidaten

---

## Quick Reference — Agent-zu-MCP-Mapping

| Agent | Primaere MCPs | Sekundaer |
|---|---|---|
| **Performance-Analyst** | Account, Campaign, Ad Group, Ad, Reporting, Insights | GAQL (Auction Insights) |
| **Search & KW-Hunter** | Reporting (search_terms), Keyword, Ad, DataForSEO | Insights (underperforming_keywords) |
| **Statistiker** | GAQL (primaer), Reporting | Insights |
| **Market & Competitive** | DataForSEO (primaer), Insights (auction_insights) | GAQL |
| **Report-Composer** | — (keine MCPs, nur Tool-Outputs) | GitHub, Gmail |

---

## MCP-Endpoints (Streamable HTTP)

Alle MCP-Trigger laufen unter `https://n8n.srv867988.hstgr.cloud/mcp/<path>`. Extrahiert aus den Workflow-Backups (2026-04-17):

| Workflow | MCP-Path | Vollstaendige URL |
|---|---|---|
| Account Tools | `google-ads-account-tools` | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-account-tools` |
| Campaign Tools | `google-ads-campaign-tools` | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-campaign-tools` |
| Ad Group Tools | `google-ads-ad-group-tools` | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-ad-group-tools` |
| Ad Tools | `google-ads-ad-tools` | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-ad-tools` |
| Keyword Tools | `google-ads-keyword-tools` | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-keyword-tools` |
| Reporting Tools | `google-ads-reporting-tools` | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-reporting-tools` |
| Insights Tools | `google-ads-insights-tools` | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-insights-tools` |
| GAQL Tools | `google-ads-gaql-tools` | `https://n8n.srv867988.hstgr.cloud/mcp/google-ads-gaql-tools` |
| DataForSEO MCP v2 | `dataforseo-mcp-v2` | `https://n8n.srv867988.hstgr.cloud/mcp/dataforseo-mcp-v2` |

**Transport-Probe (2026-04-17):** `/mcp/<path>` antwortet mit HTTP 400 auf leere POSTs — das ist der Streamable-HTTP-Endpoint (existiert, erwartet valide MCP-Initialisierungs-Message). `/mcp/<path>/sse` antwortet mit HTTP 404. Interpretation: **n8n-Instanz laeuft Streamable HTTP (≥ v1.104.0 wahrscheinlich)**, SSE ist nicht exponiert.

## Security-Status (Stand 2026-04-17, post Bearer-Auth-Setup)

**Alle 9 MCP-Trigger nutzen seit 2026-04-17 Bearer-Auth.**

- **n8n-Credential:** `Google Ads Agent MCP Bearer` (ID: `idC1kOT9LEzjFFJe`, Typ: `httpBearerAuth`)
- **Ein Token fuer alle 9 Workflows** — vereinfacht Rotation und `.mcp.json`-Pflege
- **Token-Storage:** `google-ads-agent/.mcp.json` (gitignored) + in n8n-Credential hinterlegt
- **Verifiziert via Endpoint-Probes:**
  - Ohne Token → HTTP 403 Forbidden ✅
  - Falscher Token → HTTP 403 Forbidden ✅
  - Korrekter Token → HTTP 406 (Auth passed, MCP handler expects `Accept: text/event-stream`) ✅

### Fuer Claude Code Routine (Phase 6)

Token als ENV-Variable im Routine-Environment hinterlegen (`N8N_MCP_BEARER`), nicht hardcoded im Prompt. Header-Template:
```
Authorization: Bearer ${N8N_MCP_BEARER}
```

### Token-Rotation

Falls Token kompromittiert:
1. Neues Token generieren (`python -c "import secrets; print(secrets.token_urlsafe(48))"`)
2. n8n-Credential `idC1kOT9LEzjFFJe` updaten (UI oder API `PUT /api/v1/credentials/:id`)
3. `.mcp.json` updaten
4. Routine-Environment-Variable updaten

## Phase-2-Aktionen (Status 2026-04-17, abgeschlossen)

- [x] Alle 9 MCP-Workflows als JSON backuppen → `workflows/01-*.json` bis `workflows/09-*.json`
- [x] n8n-Version verifiziert (Streamable HTTP laeuft, Fabian meldet `2.16.1` aus UI)
- [x] MCP-Trigger-Paths dokumentiert
- [x] DataForSEO-Workflow identifiziert und dokumentiert (Tools 1:1 wie geplant)
- [x] Bearer-Auth-Credential in n8n angelegt (`idC1kOT9LEzjFFJe`)
- [x] Alle 9 MCP-Trigger auf `bearerAuth` umgestellt
- [x] Auth via Endpoint-Probes verifiziert (403 ohne/falsch, 406 mit korrektem Token)
- [x] `.mcp.json` im Subprojekt mit 9 Endpoints + Authorization-Header erstellt
- [x] Backups post-auth-update neu gezogen
