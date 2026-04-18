# MVV Enamic Ads — Account-Kontext (Referenz)

Kompakter Kontext-Schnipsel fuer Sub-Agents, falls sie nicht das komplette `memory/00_strategy_manifest.md` laden wollen. Fuer Tiefen-Kontext IMMER auf das Strategy-Manifest referenzieren.

## Account-Identifikation

| Feld | Wert |
|---|---|
| Customer-ID | `2011391652` |
| Login-Customer-ID | `5662771991` |
| Account-Name | MVV Enamic Ads |
| Agentur | ZweiDigital |
| Waehrung | EUR |
| Timezone | Europe/Berlin |

## Kern-Business

**B2B-Energieprodukte** fuer Industrie- und Gewerbekunden. Lead-Gen-Ziel, kein E-Commerce.

**Mindestverbrauch Zielgruppe:** ≥ 500.000 kWh/Jahr (PPA erst ab 10 Mio kWh)

**Kundenwert:** 30.000-40.000 EUR ueber 3 Jahre → bei CPA 500 EUR = ROI 60-80x

## Produkt-Portfolio (4 Strategien)

1. **Commodity Industriestrom** — Standard-Stromvertrag, Primaer-Produkt
2. **Integrierter Offsite-PPA** — PPA in Energieliefervertrag integriert, NICHT Onsite-PPA, NICHT Dach-Solar
3. **MVV Energiefonds** — Plattform-Produkt, zwei Zielgruppen (Einkaeufer vs. Trader)
4. **MVV Energy Hub** — Partner-Oekosystem (sekundaer)

## Zielgruppen (Kern)

B2B-Industrie: Geschaeftsfuehrer, Einkaufsleiter, Energiemanager, Controlling, Trader. Deutschland. ≥ 500.000 kWh/Jahr.

## Absolute No-Gos

- B2C / Privatkunden
- Studenten / Jobsuchende
- Wettbewerber-Brand-Searches (eon, rwe, vattenfall, naturstrom etc.)
- DIY / "selber machen" / Vorlagen
- Onsite-PPA (Dach-Solar) — Verwechslungsgefahr mit unserem Offsite-PPA

## KPI-Ziele

- Ziel-CPA: **30-500 EUR pro Lead**
- Max. akzeptabler CPA: 500 EUR
- Monatsbudget: 3.000-4.000 EUR
- Primaer-Ziel: Lead-Quantitaet (Skalierung vor Effizienz, solange CPA ≤ 500)

## Bidding-Strategien

- **Lead-Kampagnen:** Target CPA (≤ 500 EUR) oder Maximize Conversions
- **Traffic-Kampagnen:** Maximize Clicks mit CPC-Cap oder Target Impression Share
- **Niemals:** ROAS-basiert (kein direktes Umsatz-Tracking)

## Match-Type-Philosophie

- **Phrase Match:** Standard
- **Exact Match:** High-Intent Keywords
- **Broad Match:** nur mit kurierter Negative-Liste und enger Aufsicht
- **Reine Broad Match in Lead-Kampagnen:** NEIN

## Ampel-Thresholds (aus Strategy-Manifest)

- 🟢 GREEN: CPA ≤ 500 EUR UND Conv stabil UND keine sig. Anomalien
- 🟡 YELLOW: CPA 500-600 EUR ODER leichte Anomalien ODER 1-2 yellow campaigns
- 🔴 RED: CPA > 600 EUR ODER mehrere red campaigns ODER sig. negative Trends

## Conversion-Typen (Prioritaet)

1. Angebotsanfrage / Kontaktformular (Primaer-SQL)
2. Webinar-Anmeldung (MQL)
3. Download / Content-Interaktion (Top-of-Funnel)

## Wichtige URLs

- Industriestrom: `partner.mvv.de/energiebeschaffung/industriestrom`
- Integrierter PPA: `partner.mvv.de/energiebeschaffung/integrierter-offsite-ppa`
- MVV Energiefonds: `partner.mvv.de/energiebeschaffung/mvv-energiefonds`
- Strompreis-Content: `partner.mvv.de/energiebeschaffung/strompreis-aktuell-boerse`
- Energy Hub: `partner.mvv.de/energiebeschaffung/mvv-energy-hubpartner`

## B2B-Qualifier-Keywords (fuer Relevance-Scoring)

Positive Signale in Search-Terms / Keyword-Candidates:
- `unternehmen`, `gewerbe`, `industrie`, `b2b`
- `kwh` (unterstellt Verbrauchs-Bewusstsein)
- `angebot`, `anfrage` (Kauf-Intent)
- Branchen: `produktion`, `logistik`, `rechenzentrum`, `kommunal`

## B2C-Exclusion-Keywords

Negative Signale:
- `privat`, `haushalt`, `wohnung`, `mieter`, `eigenheim`
- `guenstig`, `billig`
- `vergleich`, `testsieger` (Preisvergleich-Intent)
- `wechseln`, `anbieterwechsel`

## Relevance-Score-Logik (fuer Search-KW-Hunter + Market-Competitive)

Pro Keyword-Kandidat:
- **B2B-Qualifier vorhanden:** +2
- **Passt zu Produkt-Portfolio A/B/C/D:** +2
- **Location-relevant (DE):** +1
- **B2C-Signal vorhanden:** -3 (disqualifiziert)
- **Wettbewerber-Brand:** -5 (disqualifiziert)

Skala: 0-5. Threshold fuer "relevant": >= 3.

## Aktive Kampagnen (Stand Feb 2026, bei jedem Run aktualisieren)

- `25-02 | DE | Traffic | Commodity Energiefonds Generic` — ENABLED
- `25-06 | DE | Traffic | Commodity PPA` — ENABLED
- 8 weitere Kampagnen pausiert (Reaktivierungs-Queue in `04_top_performers.md`)

**Hinweis:** Performance-Analyst sollte `list_campaigns` bei jedem Session-Start aufrufen und diese Liste gegen die aktuelle API-Antwort abgleichen.

## Conversion-Tracking-Hinweise

- **Conversion-Lag:** 7-30 Tage typisch (siehe `b2b-seasonality-de.md` + `kpi-definitions.md`)
- **Micro-Conversions:** Ob Whitepaper-DL als Conv gezaehlt wird: aktuell unklar, in erster Session pruefen via `list_accessible_customers` + Account-Info
- **Enhanced Conversions:** Status unklar, bei Tracking-Fragen an Fabian / Agentur eskalieren
