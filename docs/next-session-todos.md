# Next Session — Offene Todos

**Stand:** 2026-04-17 (Ende Session). MVP-Pipeline funktional (2 Test-Runs durch, Memory live auf GitHub). Phase 6 (Cloud-Routine-Deploy) ist nächster technischer Meilenstein.

## 1. Sofort-Actions im Google Ads Account (Fabian / ZweiDigital, manuell in Google Ads UI)

Diese Maßnahmen stehen konkret im [KW16-Report Abschnitt 11](../memory/reports/2026-W16-report.md#11-recommendations-priorisiert-read-only-vorschlaege) — nicht vom System automatisierbar (READ-ONLY MVP).

| Prio | Aktion | Begruendung (Daten aus KW16-Report) |
|---|---|---|
| P0 | `power purchase agreements` PHRASE → Exact-Match oder pausieren | 886 EUR Money-Burner in 14T, 0 Conv, QS 3, Post-Click BELOW_AVERAGE |
| P0 | Mobile-Bid-Modifier -100% auf Account-Level | F-001 significant_confirmed: P(H1)=99,82%, 627 Mobile-Clicks, 0 Conv in 91T |
| P0 | Offsite-PPA-Ad: Headline `MVV Energiefonds` entfernen | Falsches Produkt in Ad-Headline |
| P1 | 13 neue Hard-Negatives deployen | siehe [Negatives-Report](../memory/03_negatives.md) Abschnitt "Auto-Appended 2026-W16 v2" |
| P1 | `ppa beratung` in eigene Ad Group mit Exact-Match isolieren | Einziger Conv-Treiber (CPA 15,18 EUR), aktuell im Pool mit Money-Burner |
| P1 | Pflicht-Qualifier "ab 500.000 kWh" in alle aktiven RSA-Headlines | Top-Performer-Pattern verletzt in allen 3 aktiven RSAs |
| P1 | Landing-Page `integrierter-offsite-ppa` Review | Post-Click BELOW_AVERAGE laut Google — Hauptursache fuer QS 3 |
| P1 | Energiefonds-Status mit ZweiDigital klaeren | Seit 25.03. pausiert (23+ Tage), ~2.360 EUR entgangen |
| P2 | Neue Keywords testen: `corporate ppa` (+325% in 12M), `ppa strom` (+129% quarterly) | Markt waechst stark, MVV nicht positioniert |
| P3 | SEO-Strategie evaluieren | MVV in 0/5 Money-Keyword-SERPs organisch sichtbar |

**Nach Umsetzung:** ZweiDigital um kurzen Status-Report per Email bitten, damit KW17-Report die Actions als "umgesetzt" markieren kann (OI-W17-02).

---

## 2. Technische Tasks fuer naechste Claude-Session

### Phase 6 — Cloud-Routine deployen

**Voraussetzungen abgeschlossen:**
- ✅ `n8n-projects` auf GitHub (`F4bse-94/n8n-projects`, privat)
- ✅ `google-ads-memory` auf GitHub (`F4bse-94/google-ads-memory`, privat)
- ✅ Bearer-Auth auf allen 9 n8n-MCPs live
- ✅ Routine-Config komplett dokumentiert in [routines/weekly-report.md](../routines/weekly-report.md)

**Schritte:**
1. In `claude.ai/settings/connectors`:
   - Gmail-Connector aktivieren (Scope `send_email`)
   - GitHub-Connector aktivieren (Scope `repo` fuer `google-ads-memory`)
   - 9 Custom HTTP MCP Connectors anlegen (URLs + Bearer-Token aus `.mcp.json`)
2. In `claude.ai/code/routines`:
   - "New routine" mit Prompt aus `routines/weekly-report.md`
   - Repositories hinzufuegen: `n8n-projects` + `google-ads-memory`
   - Environment-Var `N8N_MCP_TOKEN`
   - Scheduled Trigger: Mo 07:00 Europe/Berlin
3. Smoke-Test: "Run now" klicken, Session beobachten
4. Naechster Montag: erster echter Lauf

### Architektur-Verbesserungen

| Priority | Task | Begruendung |
|---|---|---|
| **P0** | **MCP-Endpoints absichern (aktuell offen fuer PoC).** Am 2026-04-18 wurde Bearer-Auth auf allen 9 n8n MCP Triggern deaktiviert, damit claude.ai Custom Connector UI sie anbinden kann (UI unterstuetzt keine statischen Authorization-Header). Konsequenz: URLs zu `https://n8n.srv867988.hstgr.cloud/mcp/*` sind oeffentlich zugaenglich — wer die URL kennt, kann MVV Google Ads Daten abfragen. Nach erstem erfolgreichen Routine-Run (spaetestens 7 Tage) einen Auth-Layer einziehen. Favorisierter Pfad: Cloudflare Worker Proxy (Query-Param-Token, setzt dann Bearer an n8n). Alternativen: n8n Code-Node-Auth via `?token=`, oder Warten auf Header-Support im claude.ai-UI. | Kundendaten-Schutz |
| P1 | **Source-of-Truth-Konflikt Memory-Writer klaeren.** Aktuell schreibt BEIDE — Composer (inline beim Rendering) UND das Python-Script (`scripts/memory_writer.py`). Das fuehrt zu Doppelungen in `01_session_log.md` + `02_findings_log.md`. Entscheidung noetig: (a) Composer schreibt NUR JSON-Anhang, Script macht alle File-Updates, ODER (b) Composer macht beides, Script ist Backup/Recovery-Tool. Empfehlung: (a), weil deterministisch und testbar. | SoT fuer Memory-Updates |
| P1 | **WoW-Vergleich funktional verifizieren.** In v2 sind WoW-Deltas vorhanden — aber ob der Performance-Analyst wirklich zwei separate MCP-Calls macht (current + previous) ist nicht im Log sichtbar. Test: Ein Run mit expliziter "Zeig die Raw-Responses"-Anweisung. | Qualitaetssicherung |
| P2 | **GAQL-Query fuer Bundesland-Level-Geo (`user_location_view`) fixen.** In v1 und v2 hat der Call gefehlt (Sektion 6b nur Laender-Level). Muss in `performance-analyst.md` oder eigenem Skill ergaenzt werden. | Sektion 6b unvollstaendig |
| P2 | **Asset-Performance "PENDING" als "NO_DATA_AVAILABLE" statt leere Labels.** Google gibt einfach keine Ratings wenn Impressions < 5000. Composer sollte das explizit so melden statt leere Tabelle. | Report-Qualitaet |
| P3 | **Memory-Writer-Script mit besserem Dedup.** Aktuelle Regex-Logik matched manchmal zu grob (mehrspaltige Tabellen). Verbesserungs-Idee: Parse Markdown-Tabellen richtig, matche pro Zeile spezifisch die Term-Spalte. | `scripts/memory_writer.py` |

### Post-Smoke-Test Issues (KW16/2026-04-18 Cloud-Routine erster Run)

| Priority | Task | Begruendung |
|---|---|---|
| P1 | **Reporting-Workflow `geographic_performance` HTTP 400 bei Custom-Date-Range.** Der Query nutzt `WHERE segments.date DURING {{ $json.dateRange }}` — GAQL akzeptiert `DURING` aber nur mit Enum-Constants (LAST_7_DAYS etc.), NICHT mit Custom-Ranges wie `2026-04-11,2026-04-17`. Fuer Custom-Ranges muss der n8n-Workflow eine IF-Bedingung einbauen: wenn Enum -> `DURING`, wenn Custom -> `BETWEEN 'X' AND 'Y'`. Betrifft alle Reporting-Tools mit dateRange-Param (geographic, device, hourly, search_terms, budget_pacing, keyword, ad, campaign). | Reporting-MCP Robustheit |
| P1 | **Sub-Agent Stream-Timeouts haerten.** Im ersten Cloud-Run: 2x Market-Competitive + 2x Search-Keyword-Hunter Stalled-Timeouts (>600s ohne Progress). Ursachen: DataForSEO SERP-Calls sind langsam, Search-Terms-Analyse holt zu viele Rohdaten. Loesungsansaetze: (a) Sub-Agent-Scope reduzieren (weniger SERPs pro Run, Top-20 statt Top-100 Search-Terms), (b) harte Max-Duration-Boundary im Struct-Briefing (10 Min timeout + graceful partial return), (c) Composer-Rendering-Splitting in 3 Teil-Renderer (Exec+Overview / Data / Recommendations) statt einem Monster-Output. | Anthropic Stream-Idle-Timeout |
| P2 | ~~**Statistician `LAST_90_DAYS`-Enum existiert nicht in Google Ads API.**~~ **GEFIXT 2026-04-18** in `.claude/agents/statistician.md` — ab > 30 Tagen Custom-Range (`BETWEEN 'X' AND 'Y'`) statt Enum. | |

### Open Items aus KW16-Report

| OI-ID | Item | Revisit |
|---|---|---|
| OI-W17-01 | Bundesland-Level-Geo via `user_location_view` | KW17 |
| OI-W17-02 | Mobile-Bid-Modifier umgesetzt? (bei ZweiDigital) | KW17 |
| OI-W17-05 | Ecoplanet.tech Wettbewerber-Monitoring (neuer Marktteilnehmer, 61 KW-Overlaps, noch kein Paid) | KW20 |
| OI-W16-07 | Soft-Negative `strom unternehmen` Review | KW20 (10.05.2026) |
| OI-W17-03 | H-def-3 (Mo-Fr vs. Sa-So CVR, trend_only) — passives Monitoring | KW26 |

---

## 3. Post-MVP Roadmap (nicht fuer naechste Session, aber auf Radar)

### Cloud-Routines (Erweiterungen)

- **Daily Anomaly Check** — werktags 08:00 Berlin, nur Statistiker + Composer, Email/Slack-Push bei WoW-Deltas > 2 Sigma
- **On-Demand Deep-Dive** — API-Trigger, Fabian kann via HTTP POST spontan detaillierte Analyse anstossen
- **Monthly Strategy Review** — 1. Werktag des Monats 09:00, aggregiert 4 Wochen-Reports, flagged Strategy-Manifest-Update-Kandidaten

### Write-Operationen aktivieren (Post-MVP)

Sobald MVP 4-6 Wochen stabil laeuft:
- "Approve via chat" Pattern: Fabian stimmt via Slack/Email Recommendation zu, System fuehrt via MCP-Write-Tools aus
- Start mit kleinstem Risiko: Negatives-Keyword-Add (reversibel, kein Risiko)
- Dann: Bid-Modifier-Anpassung
- Spaeter: Keyword-Pause, Ad-Copy-Update

### Cross-Account-Scaling (falls MVV sich skalieren will)

- Strategy-Manifest pro Account splitten
- Mehrere Routines, je eine pro Account
- Gemeinsame Best-Practice-Library teilen

### Chat-Interface

- Claude Workspace Project mit allen 9 MCPs verbunden
- Fabian kann ad-hoc Fragen stellen ("Wie war PPA gestern?")
- Interaktive Deep-Dives
- Voraussetzung: Streamable HTTP im Workspace-MCP-Support zuverlaessig

---

## 4. Dokumentations-Lücken die noch zu schliessen sind

- [ ] Kosten-Monitoring der Routines (was kostet ein Run? Monatliche Routine-Kosten?)
- [ ] Rollback-Procedure falls Routine kaputt laeuft
- [ ] Wie man die Routine pausieren kann wenn ZweiDigital Urlaub hat
- [ ] Escalation-Path bei Data-Quality-Issues (was tun wenn Google Ads API 48h+ Lag hat?)
