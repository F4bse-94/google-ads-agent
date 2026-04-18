# Recommendations — Priorisierungs-Schema

Referenz fuer den Report-Composer zur Synthese der **Sektion 11 (Recommendations)** im Weekly Report.

**Regel:** Jede Recommendation hat 5 Felder: `Prio`, `Aktion`, `Impact`, `Effort`, `Begruendung`.
**READ-ONLY:** Alle Aktionen sind **Vorschlaege** — das System fuehrt nichts in Google Ads aus.

---

## Prio-Schema

| Prio | Auslöser (automatisch aus Sub-Agent-Outputs ableitbar) | Beispiel-Aktion |
|---|---|---|
| **P0 Critical** | Money Burner: > 100 EUR verbrannt, 0 Conv im Zeitfenster | "Pause KW 'strom unternehmen' (Spend 402 EUR, 0 Conv)" |
| **P0 Critical** | Significant negative statistical finding (Statistiker P(H1) > 99%, Effect Size gross) | "Mobile-Bid-Modifier -100% (P(H1)=99.8%, 627 Mobile-Clicks, 0 Conv in 91T)" |
| **P0 Critical** | Ad-Copy fehlt Pflicht-Qualifier "ab 500.000 kWh" in allen aktiven RSAs | "Pflicht-Qualifier 'ab 500.000 kWh' in alle aktiven RSA-Headlines" |
| **P1 High** | High-Performer + IS Lost Budget > 20% (search_budget_lost_impression_share) | "Budget erhoehen Kampagne X (CPA 340, IS Lost Budget 35%)" |
| **P1 High** | Low Quality Score (QS <= 3) + signifikanter Spend (> 200 EUR im Zeitfenster) | "Landing Page Review Kampagne Y (QS 3, Spend 280 EUR, Post-Click BELOW_AVERAGE)" |
| **P1 High** | Negative-Kandidat high priority aus Search-Keyword-Hunter | "Add Hard Negative 'xxx' (Spend 150, 0 Conv, irrelevant-category)" |
| **P1 High** | High-Performer-Keyword im gemischten Pool → isolieren in eigene Ad Group | "'ppa beratung' in eigene Ad Group mit Exact-Match isolieren (CPA 15, einziger Conv-Treiber)" |
| **P1 High** | Pausierte Kampagne mit historisch starkem Conv-Track (aus 04_top_performers.md) | "Energiefonds-Status mit Agentur klaeren (seit 25.03. pausiert, ~2.360 EUR entgangen)" |
| **P2 Medium** | Keyword-Opportunity aus Market-Competitive mit high relevance_score | "Test KW 'corporate ppa' (+325% 12M, Relevanz A)" |
| **P2 Medium** | Neuer Wettbewerber mit Paid-Aktivitaet in Money-Keywords | "Monitor xxx.de — neu in PPA-SERPs, Position 3" |
| **P3 Watch** | Soft-Negative-Beobachtungen (trend_only ohne Signifikanz) | "Review 'strom unternehmen' in KW20 — Conv-Rate driftet" |
| **P3 Watch** | SEO-Gap (nicht direkt Google-Ads, aber strategisch) | "SEO-Strategie evaluieren (0/5 Money-Keyword-SERPs organisch sichtbar)" |

---

## Impact-Schema

- **Hoch:** > 500 EUR geschaetzter Monats-Impact, oder klare Lead-Konversions-Verbesserung
- **Mittel:** 100-500 EUR geschaetzter Monats-Impact
- **Niedrig:** < 100 EUR, oder nur Effizienz-Feintuning

Der Composer schaetzt auf Basis: verbrannter Spend (bei Pause-Aktionen), hochgerechneter Zusatz-Conv (bei Budget-Erhoehung), oder Qualitaets-Verbesserung (bei QS-relevanten Aktionen).

---

## Effort-Schema

- **S (klein):** Aenderung via Ads-UI in < 15 Min
- **M (mittel):** 1-2h Arbeit (Ad-Copy-Rewrites, neue Ad Group, Landing-Page-Review)
- **L (gross):** > halben Tag, cross-team (z.B. Landing-Page-Redesign, neue Kampagnen-Struktur)

---

## Ableitungs-Regeln

Der Composer soll pro Sub-Agent-Output prueffen:

1. **Performance-Analyst → Money Burners, IS-Lost-Budget, Low-QS, Ampel-rote Kampagnen**
2. **Search-Keyword-Hunter → High-priority Negatives, High-Performer-Isolation, Ad-Copy-Audit**
3. **Statistiker → Signifikante Findings mit Action-Empfehlung**
4. **Market-Competitive → Keyword-Opportunities, neue Wettbewerber**

Pro Quelle max. 3 Top-Recommendations, um nicht in Noise zu verlieren.

## Report-Sektion 11 Output-Format

```markdown
## 11. Recommendations (priorisiert)

### P0 Critical (sofort umsetzen)
1. **<Aktion>** — Impact: <hoch/mittel/niedrig> | Effort: <S/M/L>
   *Begruendung: <1-2 Saetze mit konkreten Zahlen aus Sub-Agent-Output>*

### P1 High (diese Woche)
...

### P2 Medium (in 2-4 Wochen)
...

### P3 Watch (passiv monitoren)
...
```

Jede Recommendation referenziert die Quelle (welcher Sub-Agent hat den Data-Point geliefert).
