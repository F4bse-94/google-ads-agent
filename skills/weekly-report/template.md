# Weekly Google Ads Report — KW {{ISO_WEEK}} / {{YEAR}}

**Zeitraum:** {{START_DATE}} – {{END_DATE}}
**Account:** MVV Enamic Ads (CID `2011391652`)
**Agentur:** ZweiDigital
**Status:** {{STATUS_EMOJI}} {{STATUS_LABEL}}
**Data Age:** {{HOURS_OF_LAG}} Stunden alt
**Generiert:** {{TIMESTAMP_ISO}} via Claude Code Routine
**Report-Version:** 1.0

---

## 0. Executive Summary

| KPI | Aktuell | WoW Δ | Sig. |
|---|---|---|---|
| Spend | {{SPEND_EUR}} € | {{SPEND_WOW_PCT}} % | {{SPEND_SIG_EMOJI}} |
| Conversions | {{CONV}} | {{CONV_WOW_PCT}} % | {{CONV_SIG_EMOJI}} |
| CPA | {{CPA_EUR}} € | {{CPA_WOW_PCT}} % | {{CPA_SIG_EMOJI}} |
| Conv. Rate | {{CVR_PCT}} % | {{CVR_WOW_PCT}} pp | {{CVR_SIG_EMOJI}} |
| CTR | {{CTR_PCT}} % | {{CTR_WOW_PCT}} pp | {{CTR_SIG_EMOJI}} |

**Budget Utilization Monat-to-Date:** {{BUDGET_UTIL_PCT}} % von {{MONTHLY_BUDGET_EUR}} € — Pacing: {{PACING_STATUS}}
**Target-CPA:** ≤ 500 € | Aktuelle Durchschnitts-CPA: **{{CPA_EUR}} €**

### Headlines der Woche
1. {{HEADLINE_1}}
2. {{HEADLINE_2}}
3. {{HEADLINE_3}}

### Status-Begruendung
{{STATUS_REASONING_1_SATZ}}

---

## 1. Follow-Ups aus Vorwoche

{{FOLLOWUP_SECTION}}

---

## 2. Campaign Performance

### 2a. Overview

| Kampagne | Status | Spend | Conv | CPA | Conv.Rate | CTR | WoW Δ Spend | WoW Δ Conv | Flags |
|---|---|---|---|---|---|---|---|---|---|
{{CAMPAIGN_TABLE_ROWS}}

### 2b. Deep-Dives (auffaellige Kampagnen)

{{CAMPAIGN_DEEP_DIVES}}

### 2c. Impression Share Split

| Kampagne | Search IS | IS Lost Budget | IS Lost Rank | Diagnose |
|---|---|---|---|---|
{{IS_SPLIT_ROWS}}

**Diagnose-Logik:**
- IS Lost Budget > 20% UND gute CPA → 📈 Skalier-Kandidat (Budget erhoehen)
- IS Lost Rank > 30% → 🔧 Quality Score / Bidding pruefen
- Beides > 20% → ⚠️ fundamentale Review notwendig

---

## 3. Keyword Insights

### 3a. Money Burners (High Spend, 0 Conv)

{{MONEY_BURNERS_TABLE}}

### 3b. High Performers (Skalier-Kandidaten)

{{HIGH_PERFORMERS_TABLE}}

### 3c. Quality Score Distribution

| QS-Bucket | Anteil |
|---|---|
{{QS_DISTRIBUTION_ROWS}}

**Weighted Average QS:** {{QS_AVG}} | WoW Δ: {{QS_WOW}}

### 3d. Low-QS-Keywords mit signifikantem Spend

{{LOW_QS_HIGH_SPEND_TABLE}}

---

## 4. Search Terms Mining

### 4a. Vorgeschlagene Negatives (priorisiert)

{{NEGATIVES_CANDIDATES_TABLE}}

### 4b. Positive Search Terms (Keyword-Expansion)

{{KEYWORD_EXPANSION_TABLE}}

---

## 5. Ad Performance

### 5a. Ad Strength Distribution (RSA)

| Strength | Count |
|---|---|
{{AD_STRENGTH_ROWS}}

### 5b. Top 5 RSAs nach Conversions

{{TOP_RSAS_TABLE}}

### 5c. Bottom 5 RSAs nach CTR (> 500 Impressions)

{{BOTTOM_RSAS_TABLE}}

### 5d. Asset Performance

| Asset-Typ | Best | Good | Learning | Low |
|---|---|---|---|---|
{{ASSET_PERFORMANCE_ROWS}}

### 5e. Ad-Copy-Audit (Flags)

{{AD_COPY_FLAGS}}

---

## 6. Dimensionen

### 6a. Device

| Device | Spend | Conv | CPA | Conv.Rate |
|---|---|---|---|---|
{{DEVICE_ROWS}}

### 6b. Geographic (Top 5 / Bottom 3)

{{GEO_TOP_BOTTOM_TABLE}}

### 6c. Hourly Performance

{{HOURLY_HEATMAP_OR_TABLE}}

---

## 7. Budget Pacing & Forecast

- **Burn-Rate:** {{BURN_RATE_EUR}} €/Tag
- **Forecasted Monats-Spend:** {{FORECAST_MONTH_EUR}} € ({{FORECAST_VS_BUDGET_PCT}} % von Budget)
- **Pacing-Status:** {{PACING_STATUS_DETAIL}}
- **Empfohlene Umverteilung:** {{BUDGET_RECOMMENDATION}}

---

## 8. Statistical Validation

### Signifikanz-Matrix

| # | Hypothese | n | Test | p-Wert | 95% KI | Effect Size | Verdict |
|---|---|---|---|---|---|---|---|
{{SIGNIFICANCE_MATRIX_ROWS}}

**Multiple-Testing-Korrektur:** {{MTC_METHOD}}
**Wochentag-Korrektur:** {{WEEKDAY_CORRECTION_STATUS}}

### Sample-Size-Warnings

{{POWER_WARNINGS}}

### Trend-Tests (ueber mehrere Wochen)

{{TREND_TESTS_TABLE}}

---

## 9. Market & Competitive (DataForSEO + Auction Insights)

### 9a. Auction Insights Delta

{{AUCTION_INSIGHTS_TABLE}}

### 9b. Keyword-Volume-Trends (Top 10)

{{KW_VOLUME_TRENDS_TABLE}}

### 9c. Neue Wettbewerber in SERP

{{NEW_COMPETITORS_LIST}}

### 9d. Neue Keyword-Opportunities

{{KW_OPPORTUNITIES_TABLE}}

---

## 10. Anomalien & Trend-Breaks

### 10a. WoW-Anomalien (signifikant, wochentag-korrigiert)

{{WOW_ANOMALIES}}

### 10b. Multi-Week-Trend-Breaks (Cochran-Armitage)

{{TREND_BREAKS}}

---

## 11. Recommendations (priorisiert, READ-ONLY Vorschlaege)

| Prio | Aktion | Impact | Effort | Kampagne / Keyword | Begruendung |
|---|---|---|---|---|---|
{{RECOMMENDATIONS_TABLE}}

**Hinweis:** Diese Vorschlaege werden im MVP NICHT automatisiert ausgefuehrt. Umsetzung durch Fabian / Agentur (ZweiDigital).

---

## 12. Open Items fuer naechste Woche

| ID | Item | Grund | Benoetigte Aktion / Revisit-Zeitpunkt |
|---|---|---|---|
{{OPEN_ITEMS_TABLE}}

---

## Appendix — Methodology

- **WoW-Definition:** aktuelle 7 Tage vs. direkt vorherige 7 Tage, gleiche Wochentage verglichen
- **Statistische Tests verwendet:** {{TESTS_USED_LIST}}
- **Daten-Lag:** Google Ads API ~{{GADS_LAG_HOURS}}h | DataForSEO ~{{DFS_LAG_DAYS}}d
- **Wochentag-Korrektur:** MVV hat ~70% Traffic Mo-Fr — WoW-Vergleiche und Anomaly-Detection erfolgen wochentag-gematcht
- **Multiple-Testing-Korrektur:** {{MTC_METHOD}} ab 3 parallelen Tests

### Data Source Timestamps

| Quelle | Letzter Pull | Alter |
|---|---|---|
{{DATA_TIMESTAMPS_TABLE}}

### Strategy-Manifest-Version

Aktiv: {{STRATEGY_VERSION}} (zuletzt geaendert: {{STRATEGY_LAST_MODIFIED}})

---

*Generated by Google Ads Agent (Claude Code Routines + n8n MCPs + GitHub Memory + DataForSEO).*
*Next scheduled run: {{NEXT_RUN_ISO}}*
