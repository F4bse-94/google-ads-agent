# 00_Strategy_Manifest — TEMPLATE

> **Anleitung:** Dieses File ist die strategische Anker-Datei fuer den Multi-Agent. Es wird von Orchestrator und Sub-Agents bei JEDEM Run gelesen. Befuelle die mit `<...>` markierten Platzhalter mit deinen Account-Spezifika und commite das Ergebnis als `00_strategy_manifest.md` in dein eigenes `google-ads-memory`-Repo.
>
> **Version:** Template v2 (Memory-Schema v2) | **Stand:** _(Datum eintragen)_ | **Account:** `<ACCOUNT_NAME>` (ID: `<CUSTOMER_ID>`)
> **Agentur:** `<AGENCY_NAME_OPTIONAL>` | **Waehrung:** `<EUR|USD|...>` | **Zeitzone:** `<Europe/Berlin>` | **Login-Customer-ID:** `<LOGIN_CUSTOMER_ID_IF_MCC>`

---

## 1. Account-Kontext

| Feld | Wert |
|---|---|
| Account-Name | `<ACCOUNT_NAME>` |
| Kunden-ID | `<CUSTOMER_ID>` |
| Account-Typ | `<Einzelkonto | MCC-Subkonto>` |
| Agentur | `<AGENCY_NAME_OR_INHOUSE>` |
| Kampagnen-Naming-Konvention | `<z.B. JJ-MM | Land | Ziel | Produkt | Agentur>` |

**Aktive Kampagnen (Stand `<KW/JAHR>`):**
- `<Kampagnen-Name 1>` (ENABLED|PAUSED) — _(kurzer Status-Kommentar)_
- `<Kampagnen-Name 2>` (ENABLED|PAUSED) — _(kurzer Status-Kommentar)_
- _(weitere)_

---

## 2. Primaeres Geschaeftsziel

`<Lead-Generierung B2B | E-Commerce-Sales | Sign-Ups | App-Installs | Kombinationen ...>`

Beschreibe in 2-4 Saetzen:
- Was wird beworben (B2C / B2B, Produkt-Kategorie)
- Was ist die zentrale Conversion (Hard / Soft)
- Was ist der durchschnittliche Customer-Lifetime-Value oder Vertragswert (relevant fuer Ziel-CPA-Begruendung)

**Conversion-Typen (Prioritaet absteigend):**
1. `<Conversion 1>` — _(Sales-Qualified-Lead | Direct-Sale | ...)_
2. `<Conversion 2>` — _(MQL | Trial-Signup | ...)_
3. `<Conversion 3>` — _(Top-of-Funnel | Newsletter | ...)_

**ROI-Argument (falls Lead-Gen):** `<z.B. CLV von X EUR rechtfertigt CPA von Y EUR (= Z-fach ROI). Daher Optimierung auf Maximize Conversions oder Target CPA, nicht ROAS.>`

---

## 3. Fokus-Produkte & Strategien

### A. `<Produkt 1>`
- **Produkt:** `<kurze Beschreibung>`
- **Mindestverbrauch / Mindestbestellwert:** `<falls relevant>`
- **Zielseite:** `<URL>`
- **USP:** `<3 wichtigste Verkaufsargumente>`
- **Funnel-Ergaenzung (optional):** `<Top-of-Funnel-Content-URL falls vorhanden>`

### B. `<Produkt 2>`
- **Produkt:** _(...)_
- **Zielseite:** _(...)_
- **USP:** _(...)_

### C. `<Produkt 3>`
_(...)_

_(Weitere Produkte nach Bedarf. Halte die Liste auf max. 4-5 Hauptprodukte. Kleinere Sortimente koennen in Sektion 7 zur Kampagnen-Architektur landen.)_

---

## 4. Zielgruppen

### Primaere Zielgruppe
| Kriterium | Beschreibung |
|---|---|
| Segment | `<B2B / B2C / Mix>` |
| Geografie | `<Deutschland | DACH | EU | ...>` |
| Volumen-Kriterium | `<z.B. ≥ 500.000 kWh/Jahr, oder ≥ 50 Mitarbeiter, oder Umsatz X-Y>` |
| Unternehmenstypen / Personas | `<Aufzaehlung>` |
| Entscheider-Rollen | `<falls B2B: GF, Einkauf, Fachabteilung, ...>` |

### Persona-Matrix

| Persona | Rolle | Hauptinteresse | Relevantes Produkt |
|---|---|---|---|
| `<Persona 1>` | `<Rolle>` | `<Pain-Point / Need>` | `<Produkt-Mapping>` |
| `<Persona 2>` | `<Rolle>` | `<Pain-Point / Need>` | `<Produkt-Mapping>` |
| _(weitere)_ | | | |

---

## 5. Absolute No-Gos & Negative-Keyword-Liste (kontoweite Ausschluesse)

> **Diese Sektion ist Single-Source-of-Truth fuer kontoweite Negatives.** Composer ergaenzt nach jedem Run um neue High-Priority-Kandidaten aus Search-Term-Mining (siehe Composer-Prompt: append-with-dedupe in die jeweilige Kategorie). Existierende Eintraege werden NIE entfernt — nur ergaenzt.

### 5.1 Ausgeschlossene Zielgruppen (strategisch)
- `<z.B. Privatkunden (B2C) bei B2B-Account>`
- `<z.B. Studenten / Auszubildende, falls kein Bildungsangebot>`
- `<z.B. Wettbewerber-Brands, wenn Bid-on-Brand nicht gewollt>`

### 5.2 Negative-Keyword-Kategorien

| Kategorie | Keywords (alphabetisch dedupliziert) |
|---|---|
| **Privatkunden / B2C** | _(z.B. haushalt, privat, wohnung, zuhause)_ |
| **Kleinverbraucher / Discount** | _(z.B. billig, gratis, vergleich)_ |
| **Ausbildung / Studium** | _(z.B. ausbildung, praktikum, seminar, studium)_ |
| **Wettbewerber-Brand** | _(deine Wettbewerber-Brands)_ |
| **Nicht-relevante Intentionen** | _(z.B. diy, kostenlos, selber machen)_ |
| _(weitere produkt-spezifische Kategorien)_ | _(...)_ |

**Hinweise zu Match-Type / Kontroll-Mechanismen:**
_(Beispiel: Generische High-Risk-Terme wie `xy` werden nicht kontoweit als Negative geschaltet, sondern via Phrase-Match-Philosophie und Ad-Group-spezifische Negatives kontrolliert.)_

---

## 6. Budget & KPI-Leitplanken

| KPI | Wert |
|---|---|
| Monatliches Gesamtbudget | `<EUR X-Y>` |
| Primaeres Ziel | `<Lead-Skalierung | Effizienz | ROAS | ...>` |
| Sekundaeres Ziel | _(...)_ |
| Ziel-CPA (Orientierung) | `<X-Y EUR pro Conversion>` |
| Max. akzeptabler CPA | `<EUR>` |
| Ziel-ROAS (falls E-Commerce) | `<x.x>` |
| Wachstumsstrategie | `<Skalieren | Halten | Konsolidieren>` |

### Ampel-Schwellen fuer Weekly-Report

Das Reporting-System nutzt diese Werte fuer Status-Ampeln (siehe `docs/report-anatomy.md`):

- 🟢 **GREEN:** CPA ≤ `<X>` EUR UND Conv-Volumen im Plan UND keine signifikanten Anomalien
- 🟡 **YELLOW:** CPA `<X-Y>` EUR ODER leichte Anomalien ODER 1-2 Yellow-Kampagnen
- 🔴 **RED:** CPA > `<Y>` EUR ODER mehrere Red-Kampagnen ODER signifikante negative Trends

---

## 7. Kampagnen-Architektur (Soll-Zustand)

```
<Account-Name> (<CUSTOMER_ID>)
│
├── LEADS / SALES (Primaer)
│   ├── [Lead] <Produkt 1> — High Intent
│   ├── [Lead] <Produkt 2> — High Intent
│   └── [Lead] <Produkt 3> — Persona-Split
│
├── TRAFFIC / CONSIDERATION (Mid-Funnel)
│   ├── [Traffic] Generic — Awareness
│   └── [Traffic] Blog / Content
│
└── BRAND (optional)
    └── [Brand] <Eigene Marke> — Markenschutz
```

---

## 8. Operative Leitplanken

### Bidding-Strategie
- **Lead-Kampagnen:** `<Target CPA | Maximize Conversions | Maximize Conversion Value>`
- **Traffic-Kampagnen:** `<Maximize Clicks mit CPC-Cap | Target Impression Share>`
- _(Akzeptierte vs. nicht-akzeptierte Strategien begruenden)_

### Match-Type-Philosophie
- **Phrase Match** als Standard fuer kontrollierte Reichweite
- **Exact Match** fuer High-Intent-Keywords (z.B. `[<produkt> angebot]`)
- **Broad Match** nur in isolierten Test-Kampagnen mit engem Negative-Keyword-Schutz
- **Kein reines Broad Match** in Lead-Kampagnen ohne Aufsicht

### Qualitaetssicherung-Rhythmus
- Woechentlich: Weekly Report (via Claude Code Routine, _(Wochentag/Uhrzeit)_) — inkl. Search-Terms-Mining
- Monatlich: Deep-Dive Anomaly-Check auf CPA-Ausreisser
- Quartalsweise: Keyword-Expansion via DataForSEO
- Quartalsweise: Strategy-Manifest-Review (diese Datei, insb. Sektion 5)

---

## 9. Strategische Prioritaeten `<JAHR>`

| Prio | Massnahme | Produkt | Status |
|---|---|---|---|
| 1 | `<Massnahme>` | `<Produkt>` | offen |
| 2 | `<Massnahme>` | `<Produkt>` | offen |
| _(...)_ | | | |

---

## 10. Memory-Schema (v2)

Drei Memory-Files im google-ads-memory-Repo:

| File | Zweck | Schreib-Regel |
|---|---|---|
| `00_strategy_manifest.md` (diese Datei) | Strategischer Anker, Pflicht-Negatives, Produkte, KPI-Schwellen | **Manuell.** Composer ergaenzt NUR Sektion 5.2 mit neuen High-Priority-Negatives (append-with-dedupe in passende Kategorie). Quartalsweise menschlicher Review. |
| `02_findings_log.md` | Hypothesen-Tracking, Statistiker-Verdicts mit IDs (F-001...) | **Composer-managed.** open_hypotheses_resolved aus stat_json wird durchgezogen, neue Items appendet. |
| `03_pending_actions.md` | Offene P0/P1-Recommendations aus letzten Wochenreports | **Composer-managed.** Letzte 4 Wochen aktiv, aeltere ins Archiv. Du markierst mit `[x]` wenn umgesetzt. |

**Reports unter `reports/<iso_week>-report.md`** sind die vollstaendige Daten-Wahrheit pro Woche.

---

*Dieses Manifest dient als strategische Grundlage fuer alle Kampagnen-Entscheidungen, Optimierungen und Reports. Es ist ein lebendes Dokument — quartalsweise pruefen, bei strategischem Pivot sofort updaten.*
