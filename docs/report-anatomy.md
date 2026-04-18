# Report Anatomy — 12-Sektionen-Template

Der Weekly Google Ads Report folgt einer **fixen Struktur** mit 12 Sektionen plus Appendix. Konsistenz ueber Wochen = Vergleichbarkeit. Auch wenn eine Sektion in einer Woche leer ist, bleibt sie im Report enthalten (markiert als "— keine Findings").

**Template-Datei (Quelle):** `skills/weekly-report/template.md` (wird in Phase 4 angelegt).

---

## Report-Header

```markdown
# Weekly Google Ads Report — KW {{ISO_WEEK}} / {{YEAR}}
**Zeitraum:** {{START_DATE}} – {{END_DATE}}
**Account:** MVV Enamic Ads (CID 2011391652)
**Status:** 🟢 GREEN | 🟡 YELLOW | 🔴 RED
**Data Age:** {{HOURS}} Stunden alt
**Generiert:** {{TIMESTAMP}} via Claude Code Routine
**Report-Version:** 1.0
```

**Status-Ampel-Kriterien:**
- 🟢 GREEN: CPA <= Target UND Conv-Volumen im Ziel UND keine Anomalien
- 🟡 YELLOW: CPA <= Target*1.2 ODER leichte Anomalien ODER 1-2 Yellow-Flag-Kampagnen
- 🔴 RED: CPA > Target*1.2 ODER mehrere Red-Flag-Kampagnen ODER signifikante negative Trends

---

## Sektion 0 — Executive Summary

**Zweck:** 1-Seiter fuer Fabian zum schnellen Lesen. Alles darunter ist optional-Tiefe.

**Inhalt:**
- 4 Zeilen Kennzahlen (Spend / Conv / CPA / Conv-Rate) mit WoW-Delta und Signifikanz-Flag (✅/🟡/⚠️)
- Budget Utilization Monat-to-Date + Pacing-Status
- 3 Headline-Findings (max. je 1 Satz)
- Status-Ampel mit 1-Satz-Begruendung

**Daten-Quelle:** Performance-Analyst `exec_kpis` + Statistiker `significance_matrix`
**Memory-Reads:** `00_strategy_manifest.md` (fuer Target-CPA)

---

## Sektion 1 — Follow-Ups aus Vorwoche

**Zweck:** System zeigt Lernfaehigkeit. Offene Items aus Vorwoche werden explizit verfolgt.

**Inhalt:**
- Tabelle: `| ID | Item (Vorwoche) | Status | Action |`
- Status-Werte: `resolved` | `still_open` | `escalated` | `dropped_with_reason`

**Bei Woche 1 (MVP-Start):** Sektion bleibt leer mit Hinweis "Erste Session — keine Follow-Ups aus Vorwoche."

**Daten-Quelle:** Statistiker `open_hypotheses_resolved` + Orchestrator liest `memory/02_findings_log.md`
**Memory-Reads:** `02_findings_log.md`

---

## Sektion 2 — Campaign Performance

### 2a. Top-Level-Tabelle

`| Kampagne | Status | Spend | Conv | CPA | Conv.Rate | CTR | IS Lost (Budget) | IS Lost (Rank) | WoW Δ Spend | WoW Δ Conv |`

Status-Ampeln pro Kampagne (gleiche Kriterien wie Report-Status).

### 2b. Deep-Dives (nur auffaellige Kampagnen)

Fuer jede Yellow/Red-Kampagne:
- Was ist auffaellig?
- Statistische Signifikanz der Abweichung
- Kontext aus Strategy-Manifest

### 2c. Impression Share Split

`| Kampagne | Search IS | IS Lost Budget | IS Lost Rank | Diagnose |`

**Diagnose-Logik:**
- IS Lost Budget > 20% UND Kampagne hat gute CPA → Skalieren-Kandidat
- IS Lost Rank > 30% → Quality-Score-Problem, Bidding-Problem
- Beides > 20% → fundamentale Review noetig

**Daten-Quelle:** Performance-Analyst `campaigns` + `budget_pacing`

---

## Sektion 3 — Keyword Insights

### 3a. Money Burners
Keywords mit >10 Clicks und 0 Conversions.

### 3b. High Performers (Skalier-Kandidaten)
Keywords mit gutem CPA UND IS Lost Budget > 20%.

### 3c. Quality Score Distribution
Balkendiagramm (als Markdown-Tabelle) + WoW-Trend.

### 3d. Low-QS-Keywords mit signifikantem Spend
QS ≤ 5 UND Spend > 50 EUR (Schwelle aus Strategy-Manifest).

**Daten-Quelle:** Search & KW-Hunter `money_burners`, `high_performers_skalierbar` + Performance-Analyst `quality_score`

---

## Sektion 4 — Search Terms Mining

### 4a. Negative-Kandidaten
Priorisiert nach Spend. Kategorisiert (B2C, Jobs, Competitor, Irrelevant, Brand-Variant).

### 4b. Positive Search Terms
Suchbegriffe mit guten Conv, die noch nicht als Keyword existieren → Expansion-Kandidat.

**Daten-Quelle:** Search & KW-Hunter `negatives_candidates`, `keyword_opportunities`
**Memory-Reads:** `03_negatives.md` (fuer Deduplizierung gegen bereits bekannte Negatives)

---

## Sektion 5 — Ad Performance

### 5a. Ad Strength Distribution
Anteil Excellent / Good / Average / Poor bei Responsive Search Ads.

### 5b. Top/Bottom RSAs
- Top 5 nach Conversions
- Bottom 5 nach CTR

### 5c. Asset Performance
Sitelinks / Callouts / Structured Snippets — Performance-Labels von Google.

**Daten-Quelle:** Performance-Analyst `ads.asset_performance` + Search & KW-Hunter `ad_copy_audit`

---

## Sektion 6 — Dimensionen

### 6a. Device (Mobile / Desktop / Tablet)
Conv-Rate, CPA, Spend-Anteil je Device.

### 6b. Geographic
Top-Regionen + Underperformer.

### 6c. Daypart (Hourly Performance)
24h-Breakdown, besonders relevant fuer B2B (Bueroeffnungszeiten).

**Daten-Quelle:** Performance-Analyst `dimensions`

---

## Sektion 7 — Budget Pacing & Forecast

- Aktueller Burn-Rate (Spend/Tag)
- Forecasted Monats-Spend (basierend auf Burn-Rate * verbleibende Tage)
- Budget-Umverteilungs-Empfehlung (wenn Pacing ≠ on_track)

**Daten-Quelle:** Performance-Analyst `budget_pacing`

---

## Sektion 8 — Statistical Validation

**Signifikanz-Matrix-Tabelle:**

`| # | Hypothese | n | Test | p-Wert | 95% KI | Effect Size | Verdict |`

**Zusatz-Infos:**
- Multiple-Testing-Korrektur: Bonferroni / FDR / none — angewendet bei >2 parallele Tests
- Wochentag-Korrektur: angewendet / not applicable
- Sample-Size-Warnings: Liste von Hypothesen mit n < required_for_80_power
- Trend-Tests (wenn vorhanden): Cochran-Armitage ueber mehrere Wochen

**Daten-Quelle:** Statistiker komplett (`significance_matrix`, `corrections_applied`, `power_warnings`, `trend_tests`)

---

## Sektion 9 — Market & Competitive (DataForSEO)

### 9a. Auction Insights Delta
Impression-Share- und Position-Entwicklung vs. Top-Konkurrenten.

### 9b. Keyword-Volume-Trends (Top 10)
Wie bewegt sich Such-Volumen unserer Top-Keywords?

### 9c. Neue Competitor im SERP
Domains, die neu fuer unsere Money-Keywords ranken.

### 9d. Neue Keyword-Opportunities
Verwandte Keywords mit Volumen, die wir nicht biddern, relevance_score > 6.

**Daten-Quelle:** Market & Competitive komplett

---

## Sektion 10 — Anomalien & Trend-Breaks

### 10a. WoW-Anomalien (signifikant, wochentag-korrigiert)
Liste der signifikanten Abweichungen vs. Vorwoche.

### 10b. Multi-Week-Trend-Breaks
Cochran-Armitage-Tests, wo sich eine 3+ Wochen stabile Entwicklung gebrochen hat.

**Daten-Quelle:** Statistiker `trend_tests` + Performance-Analyst Anomaly-Markers

---

## Sektion 11 — Recommendations (priorisiert, READ-ONLY)

**Im MVP:** rein textuelle Empfehlungen, keine automatisierte Ausfuehrung.

**Tabelle:** `| Prio | Aktion | Impact-Schaetzung | Effort | Kampagne/KW | Begruendung |`

**Prio-Skala:**
- P0 Critical — Geld wird verbrannt (Money Burners)
- P1 High — Signifikante Optimierung moeglich
- P2 Medium — Nice-to-have Verbesserung
- P3 Low — Experiment/Test-Idee

**Quellen-Mix:**
- Money Burners → P0 Pause-Empfehlung
- High-Performers mit IS Lost Budget → P1 Skalier-Empfehlung
- Low QS-Keywords → P1 Landing-Page/Ad-Relevance-Review
- Negative-Kandidaten → P1 Negative-Add
- Keyword-Opportunities → P2/P3 Test-Empfehlung

---

## Sektion 12 — Open Items fuer naechste Woche

Items die:
- Mehr Daten brauchen (`insufficient_data` vom Statistiker)
- Eine Woche Abwarten brauchen (Trend noch zu kurz)
- Externe Antwort brauchen ("Agentur soll X bestaetigen")

**Format:** `| ID | Item | Reason | Required Action / When to Revisit |`

**Daten-Quelle:** Statistiker `new_open_hypotheses` + Orchestrator-Logik

---

## Appendix — Methodology

Statisch am Ende jedes Reports:

- **Zeitraum-Definitionen:** WoW = 7 Tage aktuell vs. 7 Tage davor; LAST_7_DAYS folgt Google-Ads-Timezone
- **Statistische Tests:** Z-Test (CVR), Welch-t-Test (CPA), Cochran-Armitage (Trends), Bonferroni (Multiple Testing)
- **Daten-Grenzen:** Google Ads API hat ~24h Lag; DataForSEO ~7d Lag fuer Volume-Trends
- **Data Source Timestamps:** Zeitstempel aller Tool-Responses (fuer Audit)

---

## Memory-Updates nach Report-Generation

Der **Memory-Writer-Tool** (deterministisch, kein LLM) updatet nach Report:

| File | Update-Logik |
|---|---|
| `01_session_log.md` | Append neuer Session-Entry (max. 12 rollierend, aeltere archivieren) |
| `02_findings_log.md` | Append neue Hypothesen (Status `open`), Update alter (Status `resolved`/`still_open`) |
| `03_negatives.md` | Append neue Negatives (dedupliziert, mit Kategorie und Datum) |
| `04_top_performers.md` | Append neue Top-Performers-Eintraege (Keyword, Ad, Kampagne mit KPIs und Datum) |
| `reports/YYYY-WNN-report.md` | Der komplette Report selbst |

---

## Report-Qualitaets-Checkliste (fuer Composer)

Vor Email-Versand Self-Check:

- [ ] Alle 12 Sektionen + Header + Appendix vorhanden
- [ ] Keine `{{PLACEHOLDER}}` mehr drin
- [ ] Status-Ampel gesetzt
- [ ] Executive-Summary hat genau 3 Headlines
- [ ] Statistik-Tabelle hat bei jeder Hypothese: n, Test, p, KI, Effect-Size, Verdict
- [ ] Recommendations haben Prio-Labels
- [ ] Data-Age-Warning wenn > 36h
- [ ] Sprachstil: Deutsch, sachlich, keine Marketing-Floskeln
