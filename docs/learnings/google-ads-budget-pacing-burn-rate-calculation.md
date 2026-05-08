# Google Ads budget_pacing — burn_rate / forecast / pacing_status selbst berechnen

**Datum:** 2026-05-08 | **Kontext:** KW18-Post-Mortem Sektion 7

## Problem

Der `budget_pacing` MCP-Endpoint im Workflow `06-reporting-tools.json` liefert per Default nur Roh-Felder:
- `metrics_costMicros` (cumulativer Spend des Zeitfensters)
- `campaignBudget_amountMicros` (Tagesbudget)
- `campaign_name`

Im Report-Template wird aber `burn_rate`, `forecast`, `pacing_status` erwartet. Da das Tool diese nicht liefert, schrieb der Composer korrekt `DATA_UNAVAILABLE`.

## Loesung: Berechnung im Format-Code-Node

Im `Format Reporting Results` Code-Node wird `budget_pacing` an seiner Daten-Shape erkannt (campaignBudget present + keine ad/keyword/term-Felder). Dann werden 4 Felder ergaenzt:

```javascript
const dayOfMonth = new Date().getUTCDate();
const lastDayOfMonth = new Date(Date.UTC(y, m + 1, 0)).getUTCDate();
const cost = costMicros / 1e6;
const dailyBudget = amountMicros / 1e6;
const burnRate = cost / dayOfMonth;            // EUR/Tag bisher
const monthlyBudget = dailyBudget * lastDayOfMonth;
const forecast = burnRate * lastDayOfMonth;    // hochgerechnet auf Monatsende

// pacing_status: Kategorial
let status = 'on_track';
if (monthlyBudget > 0) {
  const pct = forecast / monthlyBudget;
  if (pct < 0.8) status = 'underspending';
  else if (pct > 1.2) status = 'overspending';
} else if (cost > 0) status = 'no_budget_set';
else status = 'no_spend';
```

## Wichtige Annahme

`amountMicros` aus der Google-Ads-API ist das **Tagesbudget**, nicht das Monatsbudget. `monthly_budget = daily_budget * Tage_im_Monat`. Diese Annahme gilt nur fuer Standard-Tagesbudgets — bei Cumulative-Budgets oder Shared-Budgets ist die Berechnung anders.

## Pacing-Schwellen

Konvention fuer dieses Projekt:
- `< 80%` Forecast/Budget → underspending (Skalier-Hebel oder Pause-Kandidat)
- `80–120%` → on_track
- `> 120%` → overspending (Budget-Cap noetig)

Diese Schwellen sind in `06-reporting-tools.json` Format-Code hardcoded — bei Aenderung dort updaten und in `memory/00_strategy_manifest.md` Sektion 6 dokumentieren.

## Bestaetigt durch

`budget_pacing(THIS_MONTH)` Live-Call am 2026-05-08: Aktive Kampagne `25-06 | DE | Traffic | Commodity PPA` lieferte burn_rate=101.59 EUR, forecast=3149.44 EUR bei monthly_budget=3100 EUR → status=`on_track`. Pausierte Kampagnen mit Budget aber ohne Spend → `underspending`.
