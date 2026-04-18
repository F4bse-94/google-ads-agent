# API-Quirks & Workarounds

Zentrale Referenz bekannter API-Probleme bei den im Weekly-Report genutzten MCPs. Ziel: der Agent kennt Workarounds **vor** dem ersten Call und macht kein Trial-and-Error pro Session.

**Regel:** Jeder Sub-Agent liest diese Datei bei Session-Start und wendet die Workarounds proaktiv an. Neue Quirks werden hier ergaenzt, nicht in einzelnen Agent-Prompts dupliziert.

---

## QUIRK-1 — `geographic_performance` MCP: HTTP 400 bei Custom-Date-Ranges

**Symptom:** Call an `google-ads-reporting.geographic_performance` mit `dateRange="YYYY-MM-DD,YYYY-MM-DD"` → HTTP 400 "Bad Request".

**Ursache:** Der n8n-Reporting-Workflow baut Query mit `WHERE segments.date DURING {{ $json.dateRange }}`. GAQL akzeptiert `DURING` aber NUR mit Enum-Constants (`LAST_7_DAYS`, etc.), nicht mit Custom-Ranges. Bei Custom-Ranges braucht's `BETWEEN 'X' AND 'Y'`.

**Workaround (proaktiv):** Bei Custom-Date-Ranges direkt den `google-ads-gaql` MCP nutzen:

```sql
SELECT
  geographic_view.country_criterion_id,
  geographic_view.location_type,
  campaign.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM geographic_view
WHERE segments.date BETWEEN '2026-04-11' AND '2026-04-17'
  AND metrics.impressions > 0
ORDER BY metrics.cost_micros DESC
LIMIT 100
```

**Betroffen:** Performance-Analyst (Phase 3: Dimensions-Geographic).
**Gilt analog fuer:** `device_performance`, `hourly_performance`, `search_terms`, `budget_pacing`, `keyword_performance`, `ad_performance`, `campaign_performance` — ueberall wo der Workflow `DURING` mit Custom-Range nutzt.
**Langfristfix:** n8n-Workflow mit IF-Node (Enum → DURING, Custom → BETWEEN). Siehe `docs/next-session-todos.md` Post-Smoke-Test-Issues P1.

---

## QUIRK-2 — GAQL-Date-Enums: nur bis `LAST_30_DAYS`

**Symptom:** Query mit `DURING LAST_90_DAYS` (auch `LAST_60_DAYS`, `LAST_180_DAYS`, `LAST_365_DAYS`) → HTTP 400 "Bad Request".

**Ursache:** Google Ads API kennt nur diese DATE-Enums: `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `THIS_MONTH`, `LAST_MONTH`, `THIS_WEEK_MON_TODAY`, `LAST_WEEK_MON_SUN`, `LAST_BUSINESS_WEEK`. **Keine 60/90/180/365-Tage-Enums.**

**Workaround:** Ab > 30 Tagen immer Custom-Range:

```sql
WHERE segments.date BETWEEN '2026-01-18' AND '2026-04-17'
```

Start-Datum = heute minus N Tage, End-Datum = gestern / letzte vollstaendige Daten-Grenze.

**Betroffen:** Statistiker (adaptives Zeitfenster), alle GAQL-basierten Queries mit langen Zeitfenstern.
**Status:** In `.claude/agents/statistician.md` als Pflicht-Regel dokumentiert (commit `0a2b915`).

---

## QUIRK-3 — `auction_insight_domain`-View in Google Ads API v20 entfernt

**Symptom:** GAQL-Query mit `FROM auction_insight_domain` → HTTP 400 "view does not exist" oder leere Response.

**Ursache:** Google Ads API v20 Breaking Change. Die Auction-Insights sind nicht mehr als eigener View exponiert. Details: [Learning](../../../docs/learnings/google-ads-api-v20-auction-insights.md).

**Workaround (dreistufig):**

1. **IS-Metriken via `campaign_performance`:** Die Impression-Share-Felder sind weiter verfuegbar:
   - `metrics.search_impression_share`
   - `metrics.search_top_impression_share`
   - `metrics.search_budget_lost_impression_share`
   - `metrics.search_rank_lost_impression_share`

2. **Geographic-Splits via `user_location_view`:** Fuer Bundesland-Level-Geo (statt `geographic_view` auf Laender-Ebene).

3. **Domain-Competition via DataForSEO SERP:** `serp_search` + `competitors_domain` liefert aktive Wettbewerber auf Money-Keywords.

**Betroffen:** Market-Competitive-Agent (Auction-Insights-Sektion).
**Langfristfix:** Keiner — API-Change. Als de-facto Account-Level-Metriken akzeptieren, wenn nur 1 aktive Kampagne.

---

## QUIRK-4 — DataForSEO `keyword_suggestions` 128k-Token-Limit

**Symptom:** Call an `dataforseo.keyword_suggestions` mit mehreren generic Seeds → Response >128k Zeichen → Claude-Tool-Limit ueberschritten.

**Ursache:** Bulk-Suggestions mit generic Seeds (z.B. `industriestrom`, `power purchase agreement`) liefern hunderte Vorschlaege × ~500 Byte/Entry. Tool-Cap bei Claude ist ~128k Zeichen Output.

**Workaround:**

1. **Nicht mehr als 3 Seed-Keywords** pro `keyword_suggestions`-Call.
2. **Pro Seed separat aufrufen**, nicht als Komma-Liste.
3. **Fuer breite Exploration:** stattdessen gezielte `keyword_overview`-Calls oder `related_keywords` mit `limit: 50`.
4. **Fuer Volume-Check einer Whitelist:** `search_volume` mit expliziter Keyword-Liste, kein Expansion-Mode.

**Betroffen:** Search-Keyword-Hunter, Market-Competitive.
**Pflicht:** Wenn du broad Keyword-Expansion brauchst, splitte auf 3+ sequentielle Calls statt einem Bulk-Call.

---

## QUIRK-5 — Google Ads MCP Default-Queries: fehlende Metriken

**Symptom:** Response von `campaign_performance`, `keyword_performance`, `ad_performance` enthaelt nicht: `search_impression_share`, `quality_score`, `match_type`, `all_conversions`.

**Ursache:** Die MCP-Standard-Queries im n8n-Workflow sind minimalistisch und aktivieren die Advanced-Metrics nicht.

**Workaround:** Bei Bedarf direkt `google-ads-gaql` MCP nutzen und die fehlenden Felder in die SELECT-Clause aufnehmen:

```sql
SELECT
  campaign.name,
  ad_group_criterion.keyword.text,
  ad_group_criterion.keyword.match_type,
  ad_group_criterion.quality_info.quality_score,
  ad_group_criterion.quality_info.creative_quality_score,
  ad_group_criterion.quality_info.post_click_quality_score,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.all_conversions,
  metrics.cost_micros,
  metrics.search_impression_share
FROM keyword_view
WHERE segments.date DURING LAST_7_DAYS
  AND metrics.impressions > 0
```

**Betroffen:** Performance-Analyst, Statistiker.
**Langfristfix:** n8n-Workflow-Queries erweitern. Siehe `docs/learnings/google-ads-mcp-default-queries-gaps.md`.

---

## QUIRK-6 — WoW-Vergleich: keine automatische Vorwochen-Lieferung

**Symptom:** `campaign_performance` MCP liefert nur ein Zeitfenster — kein automatisches WoW-Delta.

**Ursache:** Design-Entscheidung. Tool unterstuetzt ein `dateRange`-Param, nicht zwei parallel.

**Workaround (Pflicht):** Zwei separate Calls pro Metrik (current + previous), selbst subtrahieren:

```
Call 1: dateRange = "LAST_7_DAYS"              → metrics_current
Call 2: dateRange = "YYYY-MM-DD,YYYY-MM-DD"    → metrics_previous (7 Tage davor)

wow_delta_abs = current - previous
wow_delta_pct = (current - previous) / previous * 100
```

Bei `previous = 0` → `wow_delta_pct = null`.
Bei Previous-Call-Fehler → `wow_delta_* = null` plus `data_quality.missing_data_warnings: ["previous_period_unavailable"]`.

**Pflicht-Verifikation:** Im Output-JSON `data_quality.wow_verification` mit beiden Date-Ranges, Timestamps und `both_successful`-Flag ausfuellen.

**Betroffen:** Performance-Analyst (Pflicht), Statistiker (optional fuer Trend-Tests).
**Status:** Schon in `.claude/agents/performance-analyst.md` als Pflicht dokumentiert.

---

## QUIRK-7 — Stream-Idle-Timeouts bei langen MCP-Calls (>600s)

**Symptom:** "Stream idle timeout - partial response received" oder "Agent stalled: no progress for 600s" waehrend Sub-Agent laeuft.

**Ursache:** Anthropic-Seite: bei Agent-Execution ohne Token-Output fuer >600s wird der Stream-Context getrennt. Tritt auf bei:
- DataForSEO SERP-Aufrufen (langsame externe API)
- Large-Search-Terms-Responses (tausende Rows)
- Composer-Rendering von 15-25 KB Markdown

**Workaround:**

1. **Scope-Reduktion vorab:** Top-20 statt Top-100 Search-Terms, maximal 5 Keywords fuer DataForSEO SERP pro Batch.
2. **DataForSEO in kleinen Chunks:** pro Keyword ein Call, nicht Bulk.
3. **Bei Stream-Timeout:** Retry mit engerem Scope (automatisch vom Orchestrator handled).
4. **Fuer Composer-Rendering:** Nicht-kritische Sektionen (z.B. 9 Market, 10 Anomalien) bei grossem Output kuerzer rendern.

**Betroffen:** Market-Competitive, Search-Keyword-Hunter, Composer.
**Langfristfix:** Agent-Prompts haerten mit strikteren Max-Output-Grenzen. Siehe `docs/next-session-todos.md` Post-Smoke-Test-Issues P1.

---

## Wie dieser Katalog zu nutzen ist

**Bei Session-Start (jeder Sub-Agent):**
1. Diese Datei einmal lesen.
2. Bei jedem MCP-Call pruefen: ist ein QUIRK aus der Liste einschlaegig?
3. Wenn ja: direkt Workaround anwenden, nicht erst den 400-Error produzieren.

**Bei neuem Issue in Session:**
1. Issue kurz dokumentieren (Symptom, Ursache falls bekannt, Workaround).
2. Am Session-Ende: neuen QUIRK-Eintrag hier vorschlagen (im Report-Appendix oder Session-Summary).
3. Claude-Code-Session danach macht den Commit.

**Pflicht-Regel fuer Sub-Agents:** READ-ONLY-Boundary steht ueber allem — keine `create_*`, `update_*`, `pause_*`, `enable_*`, `remove_*`, `apply_recommendation`, `dismiss_recommendation`. Auch nicht, wenn ein Workaround theoretisch einen Write-Call einschliessen wuerde.
