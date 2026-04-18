---
name: Google Ads n8n-MCP Standard-Queries haben Luecken
description: Default-Queries in typischen n8n-Google-Ads-MCPs liefern IS, QS, Match-Type und Attribution-Felder NICHT — muessen explizit ergaenzt werden
type: reference
---

# Google Ads n8n-MCP Standard-Queries haben Luecken

**Problem:** Die meisten oeffentlichen n8n-Google-Ads-MCP-Templates (Hub-and-Spoke-Pattern mit HTTP-Request-Nodes) nutzen Default-GAQL-Queries, die die fuer **ernsthafte SEA-Analysen** kritischen Metriken NICHT enthalten.

## Typische Luecken in Default-Setup

### `campaign_performance` — Standard-Query liefert:
```sql
SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks,
       metrics.cost_micros, metrics.conversions, metrics.cost_per_conversion,
       metrics.ctr, metrics.average_cpc
FROM campaign
WHERE segments.date DURING {range}
```

**Was fehlt:**
- `metrics.search_impression_share` ← **kritisch** fuer Skalier-vs-Optimieren-Entscheidungen
- `metrics.search_budget_lost_impression_share` ← Budget-Engpass-Diagnose
- `metrics.search_rank_lost_impression_share` ← QS-Engpass-Diagnose
- `metrics.search_top_impression_share` ← Position-Qualitaet
- `metrics.all_conversions` (im Gegensatz zu "Primary" Conversions)
- `metrics.conversions_value` ← fuer ROAS
- `campaign.advertising_channel_type` ← Search vs. Display-Kontext

### `keyword_performance` — Standard-Query liefert:
```sql
SELECT ad_group_criterion.keyword.text, ad_group.name, campaign.name,
       metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM keyword_view
```

**Was fehlt:**
- `ad_group_criterion.keyword.match_type` ← **kritisch** fuer B2B-Analysen (Broad vs. Phrase vs. Exact)
- `ad_group_criterion.quality_info.quality_score` ← Account-Gesundheit
- `ad_group_criterion.quality_info.creative_quality_score` ← Ad-Relevanz-Diagnose
- `ad_group_criterion.quality_info.post_click_quality_score` ← Landing-Page-Diagnose
- `ad_group_criterion.quality_info.search_predicted_ctr` ← CTR-Erwartung

## Auswirkung im Reporting

Wenn diese Felder fehlen, kann ein Weekly-Report folgende Sektionen NICHT fuellen:

| Sektion | Was fehlt ohne Felder |
|---|---|
| Executive Summary | WoW-Deltas unmoeglich (nur per 2. Call mit custom Range) |
| Campaign Performance 2c | Impression-Share-Split leer |
| Keyword Insights 3c | Quality-Score-Distribution leer |
| Keyword Insights 3d | Low-QS-Keywords mit Spend leer |
| Recommendations P1 | Landing-Page-Review-Empfehlung ohne Basis |
| Market & Competitive 9a | Eigene IS fehlt fuer Kontext |

## Fix: Query-Bodies erweitern

Via `n8n_update_partial_workflow` (MCP-Tool) den `parameters.jsonBody` der HTTP-Request-Nodes updaten:

```json
{
  "type": "updateNode",
  "nodeName": "API: Campaign Performance",
  "updates": {
    "parameters.jsonBody": "={\n  \"query\": \"SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions, metrics.cost_per_conversion, metrics.ctr, metrics.average_cpc, metrics.conversions_value, metrics.search_impression_share, metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share, metrics.search_top_impression_share FROM campaign WHERE segments.date DURING {{ $json.dateRange }} AND campaign.status != 'REMOVED' ORDER BY metrics.cost_micros DESC\"\n}"
  }
}
```

Wichtig: der `={` Prefix ist n8n-Expression-Syntax (der Body ist ein Template). Beibehalten!

## WoW-Vergleiche: Zwei-Call-Pattern

Da `campaign_performance` nur einen Zeitraum pro Call liefert, braucht WoW zwei separate MCP-Calls:

1. Current-Period: `dateRange = "LAST_7_DAYS"` (oder `"LAST_14_DAYS"` etc.)
2. Previous-Period: `dateRange = "2026-04-03,2026-04-09"` (Custom Range mit Komma-Separator)

Dann im Sub-Agent-Prompt: `wow_delta = current - previous`, `wow_delta_pct = ...`

## Check-Regel fuer neue MCP-Setups

Bei jedem neuen n8n-Google-Ads-MCP-Deployment:
1. HTTP-Request-Node-Bodies inspizieren
2. Gegen diese Liste pruefen
3. Fehlende Felder ergaenzen BEVOR Sub-Agents gegen den Server sprechen — sonst hat der Report von Tag 1 an Luecken

## Quelle

- Google Ads API v20 Field Reference: https://developers.google.com/google-ads/api/fields/v20/overview
- Konkrete Fix-Operation im Repo: `google-ads-agent/DECISIONS.md` (Phase 5.5), `google-ads-agent/workflows/06-reporting-tools.json`
