# KPI-Definitionen

Einheitliche Definitionen aller KPIs im Weekly Report. Wird von Performance-Analyst, Statistiker und Composer konsistent verwendet.

## Basis-KPIs

### Spend
Geldwert (EUR), ausgegeben im Zeitraum. Quelle: Google Ads API `metrics.cost_micros / 1_000_000`. **Nicht** Budget, sondern tatsaechliche Kosten.

### Impressions
Wie oft eine Ad angezeigt wurde. `metrics.impressions`.

### Clicks
Anzahl Klicks auf Ad (Search Network). `metrics.clicks`.

### CTR (Click-Through-Rate)
`clicks / impressions * 100` in Prozent. Account-Benchmark fuer B2B Search: 3-8%.

### Conversions
Anzahl gezaehlter Conversion-Events gemaess Conversion-Tracking-Setup. Umfasst alle aktiven Conversion-Actions. Fuer MVV: Angebotsanfrage, Webinar-Anmeldung, Download.

### Conversion Rate (CVR)
`conversions / clicks * 100` in Prozent. B2B-typisch: 2-8%.

### CPA (Cost per Acquisition)
`spend / conversions` in EUR. Target MVV: 30-500 EUR.

### CPC (Cost per Click)
`spend / clicks` in EUR. Nur als Sekundaer-KPI — Entscheidungsgroesse ist CPA.

### ROAS (Return on Ad Spend)
Nicht getrackt fuer MVV (Lead-Gen ohne direkten Umsatz-Tracking). **Nicht** in Reports aufnehmen.

## Attribution

- **Default Conversion-Attribution:** Data-driven (wenn verfuegbar) oder Last-Click
- **Conversion-Lag:** B2B-typisch 7-30 Tage. Weekly-Report-Zahlen sind im letzten Zeitraum noch nicht final!
- **Wichtiger Hinweis:** Conversion-Zahlen der letzten 7 Tage sind UNTERSCHAETZT (Lag). Composer muss im Appendix darauf hinweisen.

## Impression Share (IS) KPIs

### Search Impression Share
`metrics.search_impression_share` — Anteil der erhaltenen Impressions ggu. moeglichen. Range 0-1. Nur fuer Search-Kampagnen.

### Search Budget Lost IS
`metrics.search_budget_lost_impression_share` — Anteil verlorener Impressions wegen zu geringem Budget.

### Search Rank Lost IS
`metrics.search_rank_lost_impression_share` — Anteil verlorener Impressions wegen zu niedrigem Ad-Rank (Gebot x Quality).

### Search Top IS
`metrics.search_top_impression_share` — Anteil Impressions auf Position 1-4 (Top-of-Page).

**Diagnose-Regeln fuer MVV:**
- IS Lost Budget > 20% UND CPA gut → Skalier-Kandidat
- IS Lost Rank > 30% → QS oder Bidding-Problem
- IS < 50% bei Lead-Kampagne → generelles Wachstums-Potential

## Quality Score

### Overall Quality Score
`ad_group_criterion.quality_info.quality_score` — 1-10 Skala je Keyword.

### Komponenten (nur via GAQL)
- **Creative Quality Score:** Ad-Copy-Relevanz
- **Post-Click Quality Score:** Landing-Page-Qualitaet
- **Search Predicted CTR:** vorhergesagte CTR

**MVV-Thresholds:**
- QS ≥ 7: gut (weiter so)
- QS 5-6: mittel (ok, aber Luft nach oben)
- QS ≤ 4 mit signifikantem Spend: Problem (Review dringend)

## Ad-Strength (RSA)

- **Excellent:** Alle Assets optimal genutzt, genug Varianten
- **Good:** Gut, aber 1-2 kleine Verbesserungen moeglich
- **Average:** Verbesserungspotenzial (mehr Headlines/Descriptions)
- **Poor:** Dringend verbessern

**MVV-Regel:** Ad-Strength `average` oder `poor` bei aktiven Lead-Kampagnen ist ein **Yellow-Flag**.

## WoW (Week-over-Week) Berechnung

- **Aktuelle Periode:** `time_window` (meist LAST_7_DAYS)
- **Vergleichs-Periode:** direkt davor (Tage -14 bis -8)
- **Wochentag-Match:** gleiche Wochentage vergleichen
- **Delta-Formeln:**
  - Absolute: `current - previous`
  - Prozent: `(current - previous) / previous * 100`
  - Bei `previous = 0`: Delta-Wert `null`, Textual-Kennzeichnung "n/a"

## Exec-KPIs (fuer Sektion 0)

Die fuenf "Executive KPIs" die in jedem Report prominent am Anfang stehen:
1. Spend (EUR)
2. Conversions (count)
3. CPA (EUR)
4. Conv. Rate (%)
5. CTR (%)

Diese immer mit WoW-Delta + Signifikanz-Emoji.

## Budget Pacing

### Burn Rate
`spend_month_to_date / days_elapsed_in_month` — EUR/Tag.

### Forecast
`burn_rate * total_days_in_month` — erwarteter Gesamt-Spend.

### Pacing-Status
- `on_track`: Forecast innerhalb ±5% von Monatsbudget
- `ahead`: Forecast > Budget + 5%
- `behind`: Forecast < Budget - 5%

## Conversion Lag (B2B-spezifisch)

Conversion-Lag-Analyse ueber GAQL:
```sql
SELECT segments.conversion_lag_bucket, metrics.all_conversions
FROM campaign
WHERE segments.date DURING LAST_90_DAYS
```

**Interpretation:** Fuer MVV erwartet:
- 0-3 Tage: 30-40% der Conversions (sofortige Anfragen)
- 4-14 Tage: 40-50% (Recherche-Phase)
- 15-30 Tage: 10-20% (lange Evaluierung)
- 30+ Tage: <10% (Re-Visit / Retargeting)

Wenn letzten 7 Tage Conv-Zahlen < 60% des Mittelwerts: **nicht** dramatisieren — Lag erklaert das.

## Einheiten-Konventionen

- **Waehrung:** EUR (aus Account-Settings)
- **Timezone:** Europe/Berlin
- **Zeitstempel:** ISO-8601 (YYYY-MM-DDTHH:MM:SSZ)
- **Datumsangaben in Report:** DE-Format (DD.MM.YYYY)
- **Kalenderwochen:** ISO 8601 (Mo-Start)
