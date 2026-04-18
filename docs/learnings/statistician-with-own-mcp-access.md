---
name: Statistiker-Agent mit eigenem MCP-Zugriff (statt durchgereichte Daten)
description: Anti-Pattern vermeiden — Orchestrator gibt dem Statistiker NICHT Daten, sondern Hypothesen. Statistiker zieht Rohdaten selbst und waehlt Zeitfenster adaptiv.
type: reference
---

# Statistiker-Agent mit eigenem MCP-Zugriff

**Gelernt aus einem frueheren Langdock-Setup:** Wenn der Orchestrator dem Statistiker Daten durchreicht (z.B. "hier die Campaign-KPIs der letzten 7 Tage, sind die signifikant unterschiedlich?"), kommen oft flache, methodisch schwache Tests heraus. Gruende:

1. Der Orchestrator hat nicht die statistische Intuition, das richtige Sample auszuwaehlen
2. Zeitfenster ist fix — Statistiker kann nicht erweitern falls Sample-Size zu klein
3. Rohdaten sind nicht verfuegbar — nur aggregierte KPIs
4. Multiple-Testing-Kontext fehlt (wie viele parallele Tests? Bonferroni?)
5. Power-Analyse unmoeglich

## Besseres Pattern: Statistiker zieht selbst

### Orchestrator-Briefing enthaelt KEINE Daten, nur Hypothesen:

```json
{
  "agent": "statistician",
  "objective": "Validiere folgende Hypothesen statistisch. Ziehe eigene Rohdaten via GAQL.",
  "hypotheses_to_test": [
    {"id": "H1", "statement": "Mobile CVR < Desktop CVR"},
    {"id": "H2", "statement": "CPA PPA != CPA Energiefonds"}
  ],
  "boundaries": {
    "time_window_start": "LAST_7_DAYS",
    "time_window_max_extension": "LAST_90_DAYS",
    "multiple_testing_correction_threshold": 3,
    "power_target": 0.80,
    "alpha": 0.05
  },
  "open_hypotheses_from_findings_log": [...]
}
```

### Statistiker-Tools umfassen Rohdaten-Zugriff:

```yaml
tools_available:
  - google-ads-gaql.execute_gaql   # PRIMAER: custom SQL-artige Queries
  - google-ads-gaql.search_stream  # fuer grosse Result-Sets
  - google-ads-reporting.*         # aggregate als Schnell-Check
  - google-ads-insights.*          # conversion_trends, anomaly_detection als Kontext
```

### Adaptives Zeitfenster-Pattern

```
1. Starte mit LAST_7_DAYS
2. Pull Sample-Size fuer Hypothese
3. Wenn n < n_required_for_80_power:
   - Erweitere auf LAST_14_DAYS, LAST_30_DAYS, LAST_90_DAYS
4. Wenn auch bei 90 Tagen unzureichend:
   - Verdict = "insufficient_data"
   - Hypothese bleibt im findings_log fuer naechste Session
   - Output enthaelt `needed_sample_size` und `estimated_days`
```

### Multiple-Testing-Korrektur obligatorisch

Bei >=3 parallelen Tests: Bonferroni. Bei >=10: Benjamini-Hochberg FDR.

Der Statistiker **dokumentiert explizit** welche Korrektur angewendet wurde:
```json
"corrections_applied": {
  "multiple_testing": "bonferroni",
  "weekday": true,
  "seasonality": false
}
```

### Re-Validation offener Items

Pflicht-Schritt: Liest `memory/02_findings_log.md` (File-System, nicht via Briefing durchgereicht). Fuer jede offene Hypothese:
1. Pruefe aktuelle Sample-Size
2. Wenn ausreichend: fuehre Test durch, setze neuen Verdict
3. Wenn nicht: behalte `insufficient_data`, aktualisiere `last_checked`

Das schafft einen **Lern-Kreislauf** ueber Sessions — Hypothesen die initial nicht testbar waren, werden geprueft sobald genug Daten akkumuliert.

## Verdict-Kategorien

| Verdict | p-Wert | Power | Aktion |
|---|---|---|---|
| `significant_confirmed` | < alpha | >= 0.80 | In Report als bestaetigt |
| `significant_confirmed_with_warning` | < alpha | < 0.80 | In Report + Warning |
| `trend_only` | alpha <= p < 0.10 | — | Beobachten, Re-Validation |
| `significant_rejected` | >= 0.10 | >= 0.80 | Hypothese verworfen |
| `insufficient_data` | — | < 0.80 | Bleibt offen, mit `needed_sample_size` |

## Ausgabe-Schema (Pflicht)

Statistiker liefert immer strukturiertes JSON:

```json
{
  "significance_matrix": [
    {
      "hypothesis_id": "H1",
      "hypothesis_text": "Mobile CVR < Desktop CVR",
      "sample_size": {"group_a": 1462, "group_b": 627},
      "test_used": "bayesian_beta_binomial",
      "p_value_or_p_h1": 0.9982,
      "ci_95": [0.0037, 0.0146],
      "effect_size": {"type": "cohens_h", "value": 0.129},
      "verdict": "significant_confirmed"
    }
  ],
  "corrections_applied": {...},
  "power_warnings": [...],
  "open_hypotheses_resolved": [...],
  "new_open_hypotheses": [...]
}
```

## Ergebnis in der Praxis

Mit diesem Pattern:
- Der Weekly-Report enthaelt eine klare Signifikanz-Matrix (Hypothese, n, Test, p, KI, Effect Size, Verdict)
- Kein false-positive `significant_confirmed` bei zu kleinen Samples
- Disziplinierte Re-Validation ueber Wochen (Bayesian-Posterior waechst mit Daten)
- Klares "strukturell unerreichbar" statt vage Aussagen

Erfahrung aus zwei Test-Runs (KW16 MVV Enamic): Der Statistiker hat korrekt erkannt, dass n=1 Mobile-Conversion nach 7 Tagen `trend_only` ist — nach Erweiterung auf 91 Tage dann `significant_confirmed` mit P(H1)=99,82%. Ohne adaptives Zeitfenster waere der Test verworfen worden.

## Anti-Pattern vermeiden

NICHT so:
```
Orchestrator: "Statistiker, hier sind die Mobile- und Desktop-CVRs der letzten 7 Tage: 0% und 1.12%. Signifikant?"

Statistiker: "Mit n=0 und n=1 laesst sich keine Aussage treffen..."
```

Sondern so:
```
Orchestrator-Briefing: {hypothesis: "Mobile CVR < Desktop", time_window_start: "LAST_7_DAYS", max_extension: "LAST_90_DAYS", power_target: 0.80}

Statistiker:
1. GAQL-Query fuer LAST_7_DAYS → n=0 Mobile-Conv, inadequate
2. Erweitere auf LAST_30_DAYS → n=0 Mobile-Conv aber 450+ Clicks
3. Bayesian Beta-Binomial → P(H1)=98%
4. Erweitere auf LAST_91_DAYS fuer Robustheit → P(H1)=99.82%
5. Verdict: significant_confirmed
```

## Quellen

- Anwendung im Repo: `google-ads-agent/.claude/agents/statistician.md`
- Hintergrund: `google-ads-agent/skills/weekly-report/references/statistical-tests.md`
- Lebender Ausgabe-Beispiel: `google-ads-agent/memory/reports/2026-W16-report.md` Sektion 8
