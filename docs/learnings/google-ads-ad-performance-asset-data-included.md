# Google Ads ad_performance — adStrength + RSA-Asset-Daten in einem Call

**Datum:** 2026-05-08 | **Kontext:** KW18-Post-Mortem Sektionen 5a / 5d

## Vorher (KW18-Bug)

Der Default-GAQL-Query von `ad_performance` lieferte nur Roh-Metriken (impressions, clicks, cost_micros, conversions). Es fehlten:
- `ad_strength` (fuer Sektion 5a — RSA Strength Distribution)
- `metrics.ctr` (fuer Sektion 5c — Bottom 5 RSAs by CTR)
- RSA-Headline/Description-Asset-Daten (fuer Sektion 5d — Asset Performance)

Daher 3 DATA_UNAVAILABLE im Report.

## Nachher (Fix)

GAQL erweitert in `06-reporting-tools.json` Node `API: Ad Performance`:

```sql
SELECT
  ad_group_ad.ad.id,
  ad_group_ad.ad.type,
  ad_group_ad.ad_strength,
  ad_group_ad.ad.responsive_search_ad.headlines,
  ad_group_ad.ad.responsive_search_ad.descriptions,
  ad_group_ad.ad.final_urls,
  ad_group.name, ad_group.id, campaign.name, campaign.id,
  metrics.impressions, metrics.clicks, metrics.cost_micros,
  metrics.conversions, metrics.ctr, metrics.average_cpc
FROM ad_group_ad
WHERE segments.date DURING <range>
  AND ad_group_ad.status = 'ENABLED'
  AND metrics.impressions > 0
ORDER BY metrics.cost_micros DESC LIMIT 100
```

## Was kommt zurueck

```json
{
  "adGroupAd_adStrength": "AVERAGE",
  "adGroupAd_ad_type": "RESPONSIVE_SEARCH_AD",
  "adGroupAd_ad_responsiveSearchAd_headlines": [
    { "text": "...", "assetPerformanceLabel": "PENDING|GOOD|BEST|LOW", "policySummaryInfo": {...} }
  ],
  "adGroupAd_ad_responsiveSearchAd_descriptions": [...],
  "adGroupAd_ad_finalUrls": ["https://..."],
  "metrics_ctr": 0.0309,
  "metrics_averageCpc": 11904358.95,
  "metrics_impressions": "2130",
  "metrics_clicks": "66"
}
```

## Wichtige Pflicht-Parameter

`ad_performance` MCP-Tool erfordert `dateRange`, `campaignId`, `adGroupId`. **`adGroupId=0` failed** mit `"workflow did not return a response"`. Sub-Agent muss erst `list_ad_groups(campaignId)` machen und dann pro Ad-Group iterieren.

## assetPerformanceLabel-Bedeutung

Google Ads klassifiziert Headlines/Descriptions in:
- **BEST** — bestes Ergebnis dieser Kategorie
- **GOOD** — solide Performance
- **LOW** — unterdurchschnittlich, Austausch-Kandidat
- **PENDING** — noch nicht genug Daten (typisch <5000 Impressions)
- **UNRATED** — neue Assets

Fuer den Weekly-Report Sektion 5d: Asset-Performance-Distribution = Count je Label, plus Liste der `LOW`-Assets als Optimierungs-Kandidaten.

## Bestaetigt durch

`ad_performance` Live-Call am 2026-05-08 fuer Ad-Group `180943962895` (PPA): 1 RSA mit adStrength="AVERAGE", 10 Headlines + 4 Descriptions, alle assetPerformanceLabel="PENDING" (zu wenig Daten — Ad-Group hat nur 2130 Impressions in 7 Tagen).
