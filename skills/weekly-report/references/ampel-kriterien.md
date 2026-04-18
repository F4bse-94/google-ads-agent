# Ampel-Kriterien fuer Status-Farben

Einheitliche Regeln fuer Status-Ampeln (🟢/🟡/🔴) im Weekly Report. Gilt sowohl fuer den Report-Gesamt-Status (Sektion 0) als auch fuer einzelne Kampagnen (Sektion 2a).

## Report-Gesamt-Status

### 🟢 GREEN — Alles im Plan

**Alle Bedingungen erfuellt:**
- Durchschnittliche CPA ≤ 500 EUR
- Conv-Volumen im Rahmen (kein signifikanter Einbruch vs. 4-Wochen-Schnitt)
- Keine signifikanten negativen Trends (Statistiker-Verdict)
- Budget-Pacing on_track
- Keine roten Kampagnen (max. 1 yellow OK)

### 🟡 YELLOW — Aufmerksamkeit noetig

**Mindestens eine Bedingung:**
- Durchschnittliche CPA 500-600 EUR
- Leichte negative Anomalien (p < 0.10 aber nicht < 0.05)
- Budget-Pacing behind oder ahead (>15% Abweichung)
- 1-2 yellow Kampagnen aktiv
- Signifikante Conv-Rate-Abnahme (p < 0.05 aber Effect Size klein)

### 🔴 RED — Eingriff noetig

**Mindestens eine Bedingung:**
- Durchschnittliche CPA > 600 EUR
- Mehrere rote Kampagnen gleichzeitig
- Signifikanter negativer Trend ueber 3+ Wochen (Cochran-Armitage p < 0.05)
- Money-Burner mit > 500 EUR Spend und 0 Conv
- Data-Freshness-Problem: >48h Lag
- Budget-Overrun >30%

## Kampagnen-Level-Ampel (Sektion 2a)

### 🟢 GREEN Kampagne

Alle Bedingungen:
- CPA ≤ 500 EUR
- WoW Spend-Delta zwischen -20% und +30%
- WoW Conv-Delta zwischen -20% und +50%
- IS Lost Rank < 30%
- Ad-Strength mindestens `average`

### 🟡 YELLOW Kampagne

Mindestens eine:
- CPA 500-600 EUR
- WoW Spend-Delta +30% bis +50% ODER -20% bis -30%
- WoW Conv-Delta -30% bis -50%
- IS Lost Rank 30-50%
- Ad-Strength `average` UND CPA grenzwertig
- QS-Distribution: >30% der Keywords auf QS ≤ 4

### 🔴 RED Kampagne

Mindestens eine:
- CPA > 600 EUR
- WoW Spend-Delta > +50% (Budget-Explosion)
- WoW Conv-Delta < -50% (Conv-Einbruch)
- IS Lost Rank > 50% (QS-Katastrophe)
- Ad-Strength `poor` in aktiven Lead-Kampagne
- Money-Burner-Kampagne (>500 EUR Spend, 0 Conv)

## Entscheidungsregeln fuer Composer

Der Composer berechnet den Gesamt-Status-Emoji mit dieser Logik:

```
wenn (mindestens eine RED-Bedingung erfuellt):
    gesamt_status = "🔴 RED"
sonst wenn (mindestens eine YELLOW-Bedingung erfuellt):
    gesamt_status = "🟡 YELLOW"
sonst:
    gesamt_status = "🟢 GREEN"
```

Gesamt-Status IMMER begruenden mit einer 1-Satz-Erklaerung ("Status RED weil: Kampagne X hat CPA 720 EUR bei WoW +60% Spend.").

## Ausnahmen / Interpretations-Hinweise

### Conversion-Lag-Beruecksichtigung

Wenn der aktuelle Zeitraum `LAST_7_DAYS` ist und Conv-Zahlen unterzaehlig sind (durch Lag), dann:
- Conv-basierte Metriken (CPA, Conv-Rate) werden mit einem **Lag-Adjustment-Flag** versehen
- Ampel-Entscheidung nutzt stattdessen den **LAST_14_DAYS-Wert** fuer Conv-Metriken
- Begruendung im Appendix dokumentieren

### Kleine Sample-Sizes

Wenn eine Kampagne in `time_window` weniger als 10 Conv hat:
- Ampel-Farbe wird "konservativer" gesetzt (statt RED -> YELLOW)
- Statistiker-Sample-Size-Warning muss im Report auftauchen
- Verdict "insufficient_data" ist besser als "red"

### Neue Kampagnen (Learning-Phase)

Bei Kampagnen mit < 21 Tage Laufzeit:
- CPA > 500 EUR ist KEIN automatisches YELLOW/RED
- Notation: "📖 In Learning-Phase"
- Erst nach 30 Tagen reguaelare Ampel-Kriterien

### Brand-Kampagnen (wenn aktiv)

- Brand hat typischerweise CPA < 100 EUR
- Separate Ampel-Schwelle: RED bei CPA > 200 EUR (nicht 600)
- Fokus auf Impression Share (sollte > 80% sein)

## Self-Check fuer Composer

Bevor der Report gesendet wird:

- [ ] Gesamt-Status-Emoji ist gesetzt
- [ ] Gesamt-Status hat eine 1-Satz-Begruendung in Sektion 0
- [ ] Jede Kampagne in Sektion 2a hat eine Ampel
- [ ] Rote Kampagnen in Sektion 2b Deep-Dive behandelt
- [ ] Ampel-Ausnahmen (Lag, kleine Samples, Learning-Phase) angemerkt wo zutreffend
