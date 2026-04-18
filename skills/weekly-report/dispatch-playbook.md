# Dispatch Playbook — Briefing-JSON-Schemas pro Sub-Agent

Wortwoertliche Briefing-Templates, die der Orchestrator pro Sub-Agent via Task-Tool uebergibt. Platzhalter in `{{...}}` werden vom Orchestrator gefuellt.

**Basis-Schema:** siehe `docs/handoff-contracts.md` Abschnitt "Universal Briefing-Schema".

---

## Performance-Analyst — Briefing

```json
{
  "briefing_id": "{{UUID}}",
  "orchestrator_run_id": "{{SESSION_ID}}",
  "timestamp": "{{ISO_TIMESTAMP}}",
  "agent": "performance-analyst",
  "objective": "Quantifiziere strukturelle Google-Ads-Performance der letzten 7 Tage fuer Account {{CID}}. Liefere exec_kpis, campaign_perf (mit IS-Split), ad_perf (mit Ad-Strength und Asset-Performance), device/geo/hourly, budget_pacing, quality_score_distribution. WoW-Vergleich gegen 7 Tage davor.",
  "output_schema": { "ref": "docs/handoff-contracts.md#contract-1-performance-analyst" },
  "tools_available": [
    "google-ads-account.get_account_info",
    "google-ads-campaigns.list_campaigns",
    "google-ads-ad-groups.list_ad_groups",
    "google-ads-ads.list_ads",
    "google-ads-reporting.campaign_performance",
    "google-ads-reporting.ad_performance",
    "google-ads-reporting.keyword_performance",
    "google-ads-reporting.device_performance",
    "google-ads-reporting.geographic_performance",
    "google-ads-reporting.hourly_performance",
    "google-ads-reporting.budget_pacing",
    "google-ads-insights.top_campaigns_by_cost",
    "google-ads-insights.top_campaigns_by_conversions"
  ],
  "boundaries": {
    "time_window": "LAST_7_DAYS",
    "comparison_window": "PREVIOUS_7_DAYS",
    "customer_id": "2011391652",
    "login_customer_id": "5662771991",
    "read_only": true,
    "do_not": [
      "make_recommendations",
      "perform_statistical_tests",
      "call_dataforseo_tools",
      "call_mutation_tools"
    ]
  },
  "context_from_memory": {
    "strategy_constraints": [
      "B2B only, kein Privatkunden-Traffic",
      "Target-CPA 30-500 EUR",
      "Monatsbudget ~3000-4000 EUR"
    ],
    "ampel_thresholds": {
      "green_cpa_max": 500,
      "yellow_cpa_range": [500, 600],
      "red_cpa_min": 600
    }
  }
}
```

---

## Search-Keyword-Hunter — Briefing

```json
{
  "briefing_id": "{{UUID}}",
  "orchestrator_run_id": "{{SESSION_ID}}",
  "timestamp": "{{ISO_TIMESTAMP}}",
  "agent": "search-keyword-hunter",
  "objective": "Finde (1) neue Negative-Keyword-Kandidaten aus Search-Terms der letzten 14 Tage, (2) Keyword-Opportunities via DataForSEO fuer unsere Top-5-Performer, (3) Ad-Copy-Audit-Findings gegen MVV-Top-Performer-Patterns. Dedupliziere gegen memory/03_negatives.md.",
  "output_schema": { "ref": "docs/handoff-contracts.md#contract-2-search-keyword-hunter" },
  "tools_available": [
    "google-ads-reporting.search_terms_report",
    "google-ads-reporting.keyword_performance",
    "google-ads-keywords.list_keywords",
    "google-ads-keywords.get_keyword",
    "google-ads-ads.list_ads",
    "google-ads-ads.get_ad",
    "google-ads-insights.underperforming_keywords",
    "dataforseo.keyword_suggestions",
    "dataforseo.related_keywords",
    "dataforseo.keyword_overview"
  ],
  "boundaries": {
    "time_window": "LAST_14_DAYS",
    "customer_id": "2011391652",
    "login_customer_id": "5662771991",
    "read_only": true,
    "max_dataforseo_suggestions": 50,
    "dataforseo_location_code": 2276,
    "dataforseo_language_code": "de",
    "do_not": [
      "make_pause_recommendations",
      "perform_statistical_tests",
      "call_mutation_tools"
    ]
  },
  "context_from_memory": {
    "global_negatives_categories": ["B2C", "Jobs", "DIY", "Wettbewerber", "Vergleichsportale"],
    "ad_copy_benchmarks": [
      "Lead-Qualifier 'ab 500.000 kWh' in Headline",
      "Quantifizierter Benefit wie 'bis zu 20% sparen'",
      "Produkt-Spezifitaet statt generische Slogans"
    ],
    "current_top_performer_keywords": "{{AUS_MEMORY_04}}"
  }
}
```

---

## Statistician — Briefing

```json
{
  "briefing_id": "{{UUID}}",
  "orchestrator_run_id": "{{SESSION_ID}}",
  "timestamp": "{{ISO_TIMESTAMP}}",
  "agent": "statistician",
  "objective": "Validiere folgende Hypothesen statistisch. Ziehe eigene Rohdaten via GAQL. Passe Zeitfenster adaptiv an (starte LAST_7_DAYS, erweitere bis LAST_90_DAYS bei unzureichender Sample-Size). Re-validiere offene Hypothesen aus memory/02_findings_log.md.",
  "output_schema": { "ref": "docs/handoff-contracts.md#contract-3-statistician" },
  "tools_available": [
    "google-ads-gaql.execute_gaql",
    "google-ads-gaql.search_stream",
    "google-ads-reporting.campaign_performance",
    "google-ads-reporting.device_performance",
    "google-ads-reporting.keyword_performance",
    "google-ads-insights.conversion_trends",
    "google-ads-insights.anomaly_detection"
  ],
  "boundaries": {
    "time_window_start": "LAST_7_DAYS",
    "time_window_max_extension": "LAST_90_DAYS",
    "customer_id": "2011391652",
    "login_customer_id": "5662771991",
    "read_only": true,
    "multiple_testing_correction_threshold": 3,
    "power_target": 0.80,
    "alpha": 0.05,
    "do_not": [
      "make_recommendations",
      "call_mutation_tools",
      "skip_weekday_correction_for_wow_comparisons",
      "report_without_confidence_interval"
    ]
  },
  "hypotheses_to_test": [
    {
      "id": "H-default-1",
      "statement": "Mobile CVR < Desktop CVR ueber Zeitfenster",
      "source": "default_session_hypothesis"
    },
    {
      "id": "H-default-2",
      "statement": "CPA unterscheidet sich signifikant zwischen den 2+ aktiven Kampagnen",
      "source": "default_session_hypothesis"
    },
    {
      "id": "H-default-3",
      "statement": "Broad-Match CVR < Phrase/Exact CVR",
      "source": "default_session_hypothesis"
    }
  ],
  "open_hypotheses_from_findings_log": "{{AUS_MEMORY_02}}",
  "context_from_memory": {
    "b2b_seasonality": "~70% Traffic Mo-Fr, Wochenenden schwach",
    "conversion_volume_level": "low (expected < 50 conv/week) → Bayesian bei n<30 bevorzugt",
    "strategy_constraints": ["B2B only", "Target CPA ≤ 500 EUR"]
  }
}
```

---

## Market & Competitive — Briefing

```json
{
  "briefing_id": "{{UUID}}",
  "orchestrator_run_id": "{{SESSION_ID}}",
  "timestamp": "{{ISO_TIMESTAMP}}",
  "agent": "market-competitive",
  "objective": "Liefere Markt-Aussenblick der letzten 30 Tage: (1) Auction Insights (unsere IS vs. Top-5-Wettbewerber), (2) Keyword-Volume-Trends fuer unsere Top-10-Keywords, (3) neue Wettbewerber in SERPs fuer unsere Money-Keywords, (4) neue Keyword-Opportunities mit B2B-Relevance-Score.",
  "output_schema": { "ref": "docs/handoff-contracts.md#contract-4-market-competitive" },
  "tools_available": [
    "dataforseo.keyword_overview",
    "dataforseo.search_volume",
    "dataforseo.competitors_domain",
    "dataforseo.serp_search",
    "dataforseo.ranked_keywords",
    "dataforseo.domain_overview",
    "dataforseo.related_keywords",
    "google-ads-gaql.execute_gaql",
    "google-ads-insights.get_recommendations"
  ],
  "boundaries": {
    "time_window": "LAST_30_DAYS",
    "customer_id": "2011391652",
    "login_customer_id": "5662771991",
    "read_only": true,
    "max_dataforseo_calls": 100,
    "dataforseo_location_code": 2276,
    "dataforseo_language_code": "de",
    "max_new_keyword_opportunities": 30,
    "do_not": [
      "infer_competitor_strategy",
      "benchmark_cpcs_against_competitors",
      "analyze_competitor_ad_copy",
      "call_mutation_tools"
    ]
  },
  "context_from_memory": {
    "mvv_product_landing_pages": [
      "https://partner.mvv.de/energiebeschaffung/industriestrom",
      "https://partner.mvv.de/energiebeschaffung/integrierter-offsite-ppa",
      "https://partner.mvv.de/energiebeschaffung/mvv-energiefonds",
      "https://partner.mvv.de/energiebeschaffung/mvv-energy-hubpartner",
      "https://partner.mvv.de/energiebeschaffung/strompreis-aktuell-boerse"
    ],
    "b2b_qualifier_keywords": ["unternehmen", "gewerbe", "industrie", "b2b", "kwh"],
    "b2c_exclusion_keywords": ["privat", "haushalt", "guenstig", "vergleich"],
    "current_top_keywords": "{{AUS_MEMORY_04}}"
  }
}
```

---

## Report-Composer — Briefing (Phase D)

```json
{
  "briefing_id": "{{UUID}}",
  "orchestrator_run_id": "{{SESSION_ID}}",
  "agent": "report-composer",
  "period": {
    "iso_week": "{{W}}",
    "year": "{{YYYY}}",
    "start": "{{YYYY-MM-DD}}",
    "end": "{{YYYY-MM-DD}}"
  },
  "sub_agent_outputs": {
    "performance_analyst": "{{JSON_OUTPUT}}",
    "search_keyword_hunter": "{{JSON_OUTPUT}}",
    "statistician": "{{JSON_OUTPUT}}",
    "market_competitive": "{{JSON_OUTPUT}}"
  },
  "memory_references": {
    "strategy_version": "{{AUS_00_STRATEGY_MANIFEST}}",
    "previous_week_open_items": "{{AUS_PREVIOUS_REPORT_SEKTION_12}}",
    "previous_report_path": "memory/reports/{{PREV_WEEK}}-report.md"
  },
  "output_targets": {
    "github_path": "memory/reports/{{YYYY-WNN}}-report.md",
    "commit_message": "report: Weekly Google Ads Report KW {{W}}/{{YYYY}} — Status {{STATUS_EMOJI}}",
    "email": {
      "to": "f.smogulla@gmail.com",
      "subject_template": "Weekly Google Ads Report — KW {{W}} | Status: {{STATUS_EMOJI}} {{STATUS_LABEL}}",
      "body_style": "executive_summary_html_with_github_link"
    }
  },
  "memory_writer_input": {
    "session_entry_schema": "memory/01_session_log.md#schema",
    "new_findings_source": "statistician.new_open_hypotheses + edge_case_flags",
    "resolved_findings_source": "statistician.open_hypotheses_resolved",
    "new_negatives_filter": "search_keyword_hunter.negatives_candidates WHERE priority=high",
    "new_top_performers_filter": "statistician.significance_matrix WHERE verdict=significant_confirmed AND metric IN (cpa, conversions)"
  }
}
```

---

## Orchestrator-Workflow-Summary (zur Klarheit)

```
START
  │
  ├── READ memory/00_strategy_manifest.md
  ├── READ memory/02_findings_log.md (open items)
  ├── READ memory/reports/<previous>.md (sektion 12)
  │
  ├── PARALLEL DISPATCH (via Task-Tool):
  │   ├── performance-analyst     ← Briefing #1
  │   ├── search-keyword-hunter   ← Briefing #2
  │   ├── statistician            ← Briefing #3
  │   └── market-competitive      ← Briefing #4
  │
  ├── WAIT for all 4 outputs
  ├── VALIDATE schema compliance
  │
  ├── DISPATCH report-composer    ← Briefing #5 (mit 4 sub-outputs)
  │       │
  │       ├── Render template.md
  │       ├── Git commit + push (memory-repo)
  │       ├── Gmail send_email
  │       └── Memory-Writer-Tool trigger
  │
  └── RETURN Session-Summary
END
```
