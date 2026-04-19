# Handoff Contracts — Sub-Agent Briefings

Struktur der Kommunikation zwischen Orchestrator und Sub-Agents. Ziel: keine unstrukturierten NL-Prompts an Sub-Agents — jeder bekommt ein JSON-Struct mit `objective`, `output_schema`, `tools_available`, `boundaries`, `context_from_memory`.

**Warum:** Im Langdock-Vorgaenger-System fuehrten NL-Prompts an den Statistiker zu fehlinterpretierten Ableitungen. Strukturierte Briefings fixen das.

---

## File-basierter Handoff (Pflicht ab KW17/2026)

**Grund:** Claude Code Routines haben einen dokumentierten 5-Minuten-Stream-Idle-Timeout. Inline-Passing grosser JSONs (4× ~10-25 KB) zwischen Agents erzeugt im Empfaenger-Agent eine lange Parse-/Denk-Phase ohne Token-Output → Timeout. Loesung (Anthropic-Best-Practice, siehe "How we built our multi-agent research system"): **Agents schreiben Outputs in Dateien, reichen nur Pfade weiter.**

### Staging-Directory-Konvention

- Pfad: `/tmp/w<NN>-staging/` (z.B. `/tmp/w17-staging/`) — wird vom Orchestrator **einmal** im Bootstrap angelegt (`mkdir -p`)
- Datei-Namen (fix): `performance-analyst.json`, `search-keyword-hunter.json`, `statistician.json`, `market-competitive.json`
- Format: valides JSON gemaess Contract 1-4 unten, UTF-8, LF-Zeilenenden

### Sub-Agent-Persistenz (Pflicht)

Jeder Sub-Agent schliesst seine Arbeit so ab:

1. Finales JSON-Output mit `Write`-Tool nach `/tmp/w<NN>-staging/<agent>.json` schreiben
2. An Orchestrator zurueckgeben: **nur** Pfad + 3-5-Zeilen-Summary (Status, Row-Counts, Data-Quality-Flags) — **NICHT** den Full-JSON-Dump
3. Bei Write-Fehler: Pfad leer + `error_flag` + Kurz-Ursache im Return — Orchestrator entscheidet ueber Retry

**Warum der Agent nicht den Full-JSON returnt:** Return-Payload landet im Orchestrator-Context. Bei 4 Sub-Agents × 15 KB = 60 KB Orchestrator-Context — der wird beim Composer-Dispatch weitergereicht und erzeugt genau das Problem, das wir loesen wollen.

### Orchestrator → Composer-Handoff

Composer-Briefing enthaelt **ausschliesslich** Pfade, **keine** inline JSON-Inhalte. Composer liest selbst on-demand pro Sektion (Progressive Disclosure, Details siehe `.claude/agents/report-composer.md`).

---

## Universal Briefing-Schema

Jedes Sub-Agent-Briefing folgt diesem Schema:

```json
{
  "briefing_id": "string (uuid)",
  "orchestrator_run_id": "string (linked to parent session)",
  "timestamp": "ISO-8601",
  "agent": "performance-analyst | search-keyword-hunter | statistician | market-competitive",
  "objective": "string (1-2 Saetze, was ist zu tun)",
  "output_schema": { /* agent-spezifisch, siehe unten */ },
  "tools_available": ["tool_name_1", "tool_name_2", "..."],
  "boundaries": {
    "time_window": "LAST_7_DAYS | LAST_14_DAYS | LAST_30_DAYS | CUSTOM",
    "time_window_custom": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
    "customer_id": "2011391652",
    "login_customer_id": "5662771991",
    "read_only": true,
    "do_not": ["make_recommendations", "apply_changes", "..."]
  },
  "context_from_memory": {
    "strategy_constraints": ["B2B only", "Target CPA 30-500 EUR"],
    "open_items_from_last_week": [ { "id", "hypothesis", "status" } ],
    "top_performers_reference": ["keyword_x", "ad_group_y"],
    "global_negatives_sample": ["kw1", "kw2"]
  }
}
```

---

## Contract 1: Performance-Analyst

### Objective-Beispiele
- "Quantifiziere Campaign-Level- und Ad-Level-Performance der letzten 7 Tage. Lieferer KPIs mit WoW-Vergleich."
- "Extrahiere Dimensions-Breakdown (Device, Geo, Hourly) fuer die letzten 14 Tage."

### Tools
- Read-Tools aus Account, Campaign, Ad Group, Ad, Reporting, Insights

### Output-Schema
```json
{
  "agent": "performance-analyst",
  "generated_at": "ISO-8601",
  "time_window": { "start", "end", "days" },
  "exec_kpis": {
    "spend": { "value": 0, "currency": "EUR", "wow_delta_pct": 0 },
    "conversions": { "value": 0, "wow_delta_pct": 0 },
    "cpa": { "value": 0, "target": 0, "wow_delta_pct": 0 },
    "conv_rate": { "value_pct": 0, "wow_delta_pct": 0 },
    "ctr": { "value_pct": 0, "wow_delta_pct": 0 }
  },
  "budget_pacing": {
    "monthly_budget": 0,
    "spent_month_to_date": 0,
    "burn_rate_daily": 0,
    "forecast_month_end": 0,
    "status": "on_track | ahead | behind"
  },
  "campaigns": [
    {
      "id": "string", "name": "string", "status": "ENABLED|PAUSED",
      "status_color": "green|yellow|red",
      "spend": 0, "conversions": 0, "cpa": 0, "conv_rate_pct": 0,
      "impression_share": 0,
      "is_lost_budget": 0, "is_lost_rank": 0,
      "wow_delta_spend_pct": 0, "wow_delta_conv_pct": 0,
      "wow_delta_cpa_pct": 0,
      "flags": ["low_qs_keywords", "high_impression_share_lost_budget"]
    }
  ],
  "ads": {
    "rsa_ad_strength_distribution": { "excellent": 0, "good": 0, "average": 0, "poor": 0 },
    "top_5_by_conversions": [ { "ad_id", "campaign", "ad_group", "conv", "ctr" } ],
    "bottom_5_by_ctr": [ { "ad_id", "campaign", "ad_group", "ctr", "impressions" } ],
    "asset_performance": { "sitelinks": {}, "callouts": {}, "structured_snippets": {} }
  },
  "dimensions": {
    "device": [ { "device": "mobile|desktop|tablet", "spend", "conv", "cpa", "conv_rate_pct" } ],
    "geographic": [ { "region", "spend", "conv", "cpa" } ],
    "hourly": [ { "hour_0_23", "spend", "conv" } ]
  },
  "quality_score": {
    "distribution": { "qs_1": 0, "qs_2": 0, "...": 0, "qs_10": 0 },
    "weighted_average": 0,
    "wow_delta": 0,
    "keywords_with_qs_below_5_and_spend": [ { "keyword", "qs", "spend" } ]
  },
  "data_quality": {
    "timestamp_of_latest_data": "ISO-8601",
    "hours_of_lag": 0,
    "missing_data_warnings": [],
    "wow_verification": {
      "current_range": "YYYY-MM-DD,YYYY-MM-DD",
      "previous_range": "YYYY-MM-DD,YYYY-MM-DD",
      "current_call_timestamp": "ISO-8601",
      "previous_call_timestamp": "ISO-8601",
      "current_row_count": 0,
      "previous_row_count": 0,
      "both_successful": true
    }
  }
}
```

### Boundaries (strikt)
- Kein statistischer Test (macht der Statistiker)
- Keine Empfehlungen (macht der Composer beim Rendern)
- `data_quality.wow_verification` ist PFLICHT — nie weglassen, siehe `.claude/agents/performance-analyst.md` "WoW-Verifikation"
- Keine Write-Tools anfassen

---

## Contract 2: Search & Keyword-Hunter

### Objective-Beispiele
- "Finde neue Negative-Keyword-Kandidaten aus Search-Terms der letzten 14 Tage. Priorisiere nach Spend."
- "Identifiziere Keyword-Expansion-Opportunities via DataForSEO fuer unsere Top-Performer."

### Tools
- Reporting (search_terms_report), Keyword (list, get), Ad (list, get), DataForSEO (keyword_suggestions, related_keywords, keyword_overview), Insights (underperforming_keywords)

### Output-Schema
```json
{
  "agent": "search-keyword-hunter",
  "generated_at": "ISO-8601",
  "time_window": { "start", "end", "days" },
  "negatives_candidates": [
    {
      "search_term": "string",
      "impressions": 0, "clicks": 0, "spend": 0, "conversions": 0,
      "category": "b2c | jobs | competitor | irrelevant | brand_variant",
      "priority": "high | medium | low",
      "rationale": "1 Satz Begruendung"
    }
  ],
  "keyword_opportunities": [
    {
      "keyword": "string",
      "search_volume_de": 0,
      "competition": "low | medium | high",
      "cpc_estimate": 0,
      "source": "dataforseo_suggestion | search_term_gap | top_performer_variant",
      "rationale": "string"
    }
  ],
  "money_burners": [
    { "keyword", "match_type", "spend", "clicks", "conversions": 0, "campaign", "ad_group" }
  ],
  "high_performers_skalierbar": [
    { "keyword", "conv", "cpa", "impression_share", "is_lost_budget", "potential_conv_if_scaled" }
  ],
  "ad_copy_audit": {
    "underperforming_rsas_count": 0,
    "findings": [ { "ad_id", "issue": "low_ctr | weak_headlines | missing_callout", "suggestion" } ],
    "headline_patterns_high_performers": []
  },
  "data_quality": { "...": "..." }
}
```

### Boundaries
- Keine Empfehlung "pause/add" — nur Kandidaten mit Rationale
- DataForSEO-Credits-Effizienz: max. 50 keyword_suggestions pro Run
- Match-Type-Info MUSS mitkommen (B2B-Relevanz)

---

## Contract 3: Statistiker

### Objective-Beispiele
- "Validiere folgende Hypothesen statistisch: (1) Mobile CVR signifikant schlechter als Desktop; (2) Kampagne X CPA-Verbesserung vs. Vorwoche; (3) Offenes Follow-Up aus KW15: 'Yellow-Pages-Region unterperformt' noch gueltig?"
- "Pruefe ob Trend 'sinkende Conv.Rate bei Broad-Match' ueber letzte 4 Wochen signifikant ist (Cochran-Armitage)."

### Tools
- GAQL (execute_gaql, search_stream), Reporting, Insights

### Arbeitsweise
1. Liest `memory/02_findings_log.md` selbststaendig (via File-System)
2. Formuliert Hypothesen (aus Orchestrator-Briefing + offenen Items)
3. Zieht **selbst** Rohdaten (nicht vom Orchestrator durchgereicht!)
4. Waehlt Zeitfenster adaptiv:
   - Startet mit LAST_7_DAYS
   - Bei Sample-Size <30 Conversions: erweitert auf 14/30/90 Tage
5. Fuehrt Tests:
   - CVR-Vergleich: Zwei-Proportionen Z-Test
   - CPA-Vergleich: Welch-t-Test (ungleiche Varianzen)
   - Trend-Test: Cochran-Armitage (falls 3+ Datenpunkte aus Findings-Log)
   - Sample-Size <30: Bayesian-Posterior-Analyse
6. Multiple-Testing-Korrektur: Bonferroni wenn 3+ parallele Tests
7. Power Analysis: "wie viele Conversions brauche ich noch?"

### Output-Schema
```json
{
  "agent": "statistician",
  "generated_at": "ISO-8601",
  "time_window_used": { "start", "end", "days", "adapted": true },
  "significance_matrix": [
    {
      "hypothesis_id": "H1",
      "hypothesis_text": "Mobile CVR < Desktop CVR",
      "sample_size": { "group_a": 0, "group_b": 0 },
      "test_used": "two_proportion_z_test",
      "p_value": 0,
      "ci_95": [0, 0],
      "effect_size": { "type": "cohens_h", "value": 0 },
      "verdict": "significant_confirmed | significant_rejected | trend_only | insufficient_data"
    }
  ],
  "corrections_applied": {
    "multiple_testing": "bonferroni | fdr | none",
    "weekday": true,
    "seasonality": false
  },
  "power_warnings": [
    { "hypothesis_id", "n_actual", "n_required_for_80_power", "gap" }
  ],
  "open_hypotheses_resolved": [
    { "findings_log_id", "new_verdict", "reason" }
  ],
  "new_open_hypotheses": [
    { "hypothesis", "reason_unresolved", "needed_sample_size" }
  ],
  "trend_tests": [
    {
      "metric": "conversion_rate_broad_match",
      "weeks_analyzed": 4,
      "test": "cochran_armitage",
      "chi_squared": 0,
      "p_value": 0,
      "direction": "decreasing|increasing|no_trend"
    }
  ],
  "methodology_notes": [
    "Used Welch's t-test due to unequal variances in CPA comparison",
    "Extended time window to LAST_30_DAYS for H2 because LAST_7_DAYS yielded n=4 conversions"
  ]
}
```

### Boundaries
- Keine Handlungsempfehlungen ("daher sollten wir X pausieren") — nur statistische Aussagen
- Bei `insufficient_data`: Hypothese muss in `new_open_hypotheses` mit `needed_sample_size`
- Multiple Testing Korrektur PFLICHT bei >2 parallelen Tests

---

## Contract 4: Market & Competitive

### Objective-Beispiele
- "Liefer Auction-Insights-Entwicklung der letzten 30 Tage + Competitor-SERP-Analyse fuer Top-10-Keywords."
- "Welche neuen Wettbewerber sind in den SERPs aufgetaucht? Welche Keyword-Volume-Trends zeigen unsere Money-Keywords?"

### Tools
- DataForSEO (keyword_overview, search_volume, competitors_domain, serp_search, ranked_keywords, domain_overview), GAQL (fuer auction_insights)

### Output-Schema
```json
{
  "agent": "market-competitive",
  "generated_at": "ISO-8601",
  "time_window": { "start", "end", "days": 30 },
  "auction_insights": [
    {
      "competitor_domain": "string",
      "our_impression_share": 0,
      "their_impression_share": 0,
      "our_position_avg": 0,
      "their_position_avg": 0,
      "delta_vs_last_month": { "is_pct_points", "position" }
    }
  ],
  "keyword_volume_trends": [
    {
      "keyword": "string",
      "volume_current_month": 0,
      "volume_3m_avg": 0,
      "volume_12m_avg": 0,
      "trend_direction": "up | down | stable | volatile",
      "notes": "seasonality, trending topics etc."
    }
  ],
  "new_competitors": [
    {
      "domain": "string",
      "keyword_overlap_pct": 0,
      "avg_position_on_our_kws": 0,
      "ad_presence": true,
      "first_seen_in_serp": "ISO-8601"
    }
  ],
  "new_keyword_opportunities": [
    {
      "keyword": "string",
      "volume": 0, "cpc": 0, "competition": "low|medium|high",
      "relevance_score_1_10": 0,
      "rationale": "string"
    }
  ],
  "data_quality": { "...": "..." }
}
```

### Boundaries
- Keine Write-Actions (DataForSEO ist ohnehin Read-Only)
- Max. 100 Keywords pro Run (Credit-Kontrolle)
- Relevance-Score basiert auf Strategy-Manifest (B2B-Fit pruefen)

---

## Orchestrator Self-Briefing

Der Orchestrator folgt keinem externen Briefing, aber verwaltet seinen eigenen State:

```json
{
  "session_id": "string",
  "trigger": "scheduled_weekly | manual | api",
  "iso_week": 17,
  "year": 2026,
  "memory_loaded": {
    "strategy": true,
    "findings_log": true,
    "negatives_count": 0,
    "top_performers_count": 0
  },
  "dispatched_briefings": [ /* array of 4 briefings above */ ],
  "synthesis_context": {
    "composer_input": { /* merged outputs */ },
    "report_version": "1.0"
  }
}
```

---

## Report-Composer Input (File-Referenzen, NICHT inline)

Der Composer bekommt **Pfade** zu Sub-Agent-Outputs, nicht die Outputs selbst. Er liest on-demand pro Sektion via `Read` + `jq`/Offset, um seinen Context klein zu halten.

```json
{
  "agent": "report-composer",
  "period": { "iso_week": 17, "year": 2026, "start": "2026-04-20", "end": "2026-04-26" },
  "staging_dir": "/tmp/w17-staging",
  "sub_agent_output_paths": {
    "performance_analyst": "/tmp/w17-staging/performance-analyst.json",
    "search_keyword_hunter": "/tmp/w17-staging/search-keyword-hunter.json",
    "statistician": "/tmp/w17-staging/statistician.json",
    "market_competitive": "/tmp/w17-staging/market-competitive.json"
  },
  "sub_agent_status": {
    "performance_analyst": { "ok": true, "row_counts": { "campaigns": 12, "ads": 34 }, "warnings": [] },
    "search_keyword_hunter": { "ok": true, "row_counts": { "negatives_candidates": 18, "opportunities": 6 }, "warnings": [] },
    "statistician": { "ok": true, "hypotheses_tested": 3, "warnings": ["H2 insufficient_data"] },
    "market_competitive": { "ok": true, "competitors_found": 7, "warnings": [] }
  },
  "memory_references": {
    "strategy_manifest_path": "memory/00_strategy_manifest.md",
    "findings_log_path": "memory/02_findings_log.md",
    "previous_report_path": "memory/reports/2026-W16-report.md"
  },
  "template_path": "skills/weekly-report/template.md",
  "output_targets": {
    "github_path": "memory/reports/2026-W17-report.md",
    "email": {
      "to": "f.smogulla@gmail.com",
      "subject_template": "Weekly Google Ads Report — KW {{iso_week}} | Status: {{status}}",
      "body_style": "executive_summary_only_with_github_link"
    }
  }
}
```

**Anti-Pattern (nicht mehr erlaubt):** `sub_agent_outputs: { full JSON inline }` — erzeugt Stream-Idle-Timeouts im Composer.

### Composer-Regeln
- **Kein Erfinden:** wenn Sub-Agent kein Datum lieferte, Sektion als "❗ DATA UNAVAILABLE" markieren
- **Template-Compliance:** alle 12 Sektionen vorhanden (auch wenn leer)
- **Language:** Deutsch fuer Text, Englisch fuer Metrik-Labels (CPA, CTR, CVR)
- **Tone:** sachlich, datengetrieben, kein Marketing-Speak
