---
name: Google Ads API v20 — Auction Insights Workaround
description: `auction_insight_domain` existiert in v20 nicht als Top-Level-Resource. Fallback via campaign_performance + DataForSEO
type: reference
---

# Google Ads API v20 — Auction Insights Workaround

**Problem:** In aelteren Google-Ads-API-Versionen gab es eine `auction_insight_domain` Resource fuer GAQL-Queries. In v20 ist diese NICHT mehr direkt abfragbar — `FROM auction_insight_domain` wirft einen Fehler.

## Was NICHT funktioniert (Stand v20, April 2026)

```sql
-- Diese Query schlaegt fehl:
SELECT campaign.name, auction_insight_domain.domain,
       metrics.search_impression_share
FROM auction_insight_domain
WHERE segments.date DURING LAST_30_DAYS
```

Google hat Auction Insights als Feature der UI zurueckgezogen bzw. nicht in die neue API-Struktur portiert.

## Was stattdessen funktioniert

### 1. Unsere eigene IS-Lage via `campaign`

```sql
SELECT campaign.name, campaign.status,
       metrics.search_impression_share,
       metrics.search_budget_lost_impression_share,
       metrics.search_rank_lost_impression_share,
       metrics.search_top_impression_share
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status != 'REMOVED'
```

Liefert: Wie gut bewerben wir selbst (ohne Wettbewerber-Vergleich).

### 2. Wettbewerber-Set via DataForSEO

Fuer unsere Top-5-Money-Keywords:

```python
# SERP-Snapshot
dataforseo.serp_search(
    keyword="industriestrom anbieter",
    location_code=2276,  # Germany
    language_code="de"
)
# -> Domains die in SERP + Ads erscheinen

# Competitor-Set
dataforseo.competitors_domain(
    seed_domain="partner.mvv.de",
    location_code=2276,
    language_code="de"
)
```

Liefert: Wer steht neben uns in SERPs? Wer schaltet bezahlte Ads?

### 3. Competitor-Details via DataForSEO

```python
# KW-Overlap + Traffic
dataforseo.domain_overview(
    target="eon.de",
    location_code=2276,
    language_code="de"
)

# Deren Top-Keywords
dataforseo.ranked_keywords(
    target="eon.de",
    location_code=2276,
    limit=100
)
```

Liefert: Marktanteil, Kernsegmente, Strategie-Hinweise.

## Kombination = "Pseudo-Auction-Insights"

Das ist nicht das Original-Feature, aber fuer strategische Entscheidungen gleichwertig:

| Was man wissen will | Woher |
|---|---|
| Meine eigene IS | `campaign_performance` mit IS-Feldern |
| Wer meine Wettbewerber sind | DataForSEO `competitors_domain` |
| Wie stark sie bidden | DataForSEO `serp_search` → `paid_results` |
| Wer neu im Markt ist | SERP-Snapshots vergleichen ueber Zeit |
| Meine Position-Tendenz | IS Lost Budget vs. IS Lost Rank |

## Hinweis fuer Prompts

Sub-Agents die nach Auction Insights fragen MUESSEN wissen, dass die GAQL-Query `FROM auction_insight_domain` fehlschlaegt. In `market-competitive.md`-Prompt explizit dokumentieren und auf den Fallback verweisen.

## Check ob sich das aendert

Google Ads API Versions-Roadmap: https://developers.google.com/google-ads/api/docs/release-notes

Bei Upgrade auf v21/v22 pruefen ob `auction_insight_domain_view` oder `segments.auction_insight_domain` freigeschaltet wurde.

## Quelle

- Google Ads API Reference v20: https://developers.google.com/google-ads/api/reference/rpc/v20/
- DataForSEO SERP API: https://docs.dataforseo.com/v3/serp/google/
- Anwendung im Repo: `google-ads-agent/.claude/agents/market-competitive.md`
