# n8n Format-Code-Node — Recursive Flatten ist Pflicht bei verschachtelten GAQL-Responses

**Datum:** 2026-05-08 | **Kontext:** KW18-Post-Mortem Quality-Score-Distribution

## Problem

Im KW18-Report Sektion 3c stand `DATA_UNAVAILABLE: Die Quality-Score-Verteilung wurde im Payload nicht geliefert.` Ich vermutete eine Schema-Luecke im n8n-Workflow `06-reporting-tools.json` — falsche Annahme.

Der GAQL-Query `SELECT ad_group_criterion.quality_info.quality_score ...` ist korrekt definiert. Das Problem lag im `Format Reporting Results` Code-Node, der die GAQL-Response **nur 1 Ebene tief flattete**:

```javascript
// ALT — flattet nur 1 Ebene
flattened[`${key}_${subKey}`] = subValue;  // Wert kann selbst noch ein Object sein
```

Damit wurde aus `{adGroupCriterion: {qualityInfo: {qualityScore: 5}}}` ein Output `{adGroupCriterion_qualityInfo: {qualityScore: 5}}` — das verschachtelte Object blieb in der Response, der Sub-Agent hat es schlicht uebersehen.

## Loesung: Recursive Flatten

```javascript
function flatten(obj, prefix = '', out = {}) {
  for (const [key, value] of Object.entries(obj)) {
    const newKey = prefix ? `${prefix}_${key}` : key;
    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
      flatten(value, newKey, out);
    } else {
      out[newKey] = value;
    }
  }
  return out;
}
const formatted = items[0].json.results.map(row => ({ json: flatten(row) }));
```

Daraus wird **flach**: `{ adGroupCriterion_qualityInfo_qualityScore: 5, adGroupCriterion_keyword_text: "ppa", ... }` — direkt nutzbar.

**Wichtig:** Arrays bleiben Arrays (sonst zerfallen RSA-Headlines `[{text, label}]` zu `headlines_0_text, headlines_0_label, ...`).

## Bestaetigt durch

Test mit `keyword_performance` MCP-Call: QS = 5, 5, 3, 3 als flache Number-Felder. Plus `creativeQualityScore`, `postClickQualityScore`, `searchPredictedCtr` als Strings.

## Generalisierung

Die meisten Google-Ads-GAQL-Felder sind stark verschachtelt (`ad_group_ad.ad.responsive_search_ad.headlines[].asset_performance_label`). **Default-Strategy fuer GAQL-Format-Nodes: recursive flatten + Arrays unangetastet**. Sub-Agenten nutzen dann schlicht die Snake-zu-Camel-Punkt-Pfade als flache Keys.
