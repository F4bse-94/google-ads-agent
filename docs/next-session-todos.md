# Next Session — Offene Todos

**Stand:** 2026-04-18 (Ende Session). Phase 6 Deploy weitgehend fertig — Infrastruktur steht (neuer Repo F4bse-94/google-ads-agent, Mail-Bridge als MCP, api-quirks.md, Composer haertet). **Blocking fuer naechste Session:** Fabian muss Routine-Prompt + Setup-Skript in claude.ai manuell synchronisieren (siehe Abschnitt 0), dann ersten autonomen Run starten.

Detaillierte Session-Historie: [sessions/2026-04-18-session-summary.md](sessions/2026-04-18-session-summary.md)

---

## 0. BLOCKING — Routine-Config in claude.ai aktualisieren

**Vor jedem weiteren Run, Fabian manuell:**

1. **Setup-Skript** → auf nur `pip install scipy statsmodels numpy` reduzieren (die alten `rm -rf` + `ln -sfn`-Zeilen raus)
2. **Orchestrator-Prompt** → komplett ersetzen durch Stand aus [routines/weekly-report.md](../routines/weekly-report.md) Abschnitt "Routine-Prompt". Fabian hat einen Copy-Paste-Block aus der Session-Chat-History 2026-04-18.
3. **Mail-Bridge Connector** in claude.ai angelegt (ja, erledigt ✅)
4. Speichern + Workflow aktiv lassen

**Test:** "Run now" → sollte diesmal **autonom** durchlaufen (Autonomie-Regel, Bootstrap-Symlink-Reset, Self-Fallback aktiv). Erwartung: Report in `google-ads-memory/reports/`, Email an `f.smogulla@gmail.com`, Session-Summary ohne Rueckfragen.

---


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

**Status:** Weitgehend fertig, nur claude.ai-Sync fehlt (siehe Abschnitt 0).

**Voraussetzungen abgeschlossen (2026-04-18):**
- ✅ Repo-Split: eigener Repo `F4bse-94/google-ads-agent` (Fresh Commit, keine History-Uebernahme aus n8n-projects)
- ✅ `google-ads-memory` Repo live auf GitHub, als Submodule im neuen Repo
- ✅ 10 claude.ai-Connectors angelegt (Gmail, GitHub, 8 Google-Ads-MCPs, DataForSEO, Mail-Bridge MCP)
- ✅ Bearer-Auth auf allen n8n-MCPs **deaktiviert** (PoC-Kompromiss — Security-Todo s.u.)
- ✅ Mail-Bridge als MCP-Workflow (`MWsWFnQubZ1Z21QL`, Path `/mcp/mail-bridge`) statt Gmail-Connector (der nur `create_draft` bietet)
- ✅ Gmail OAuth2 Credential in n8n (`WuFfkaTplA3haMId`, `fabian.smog@googlemail.com`)
- ✅ Composer-Robustheit: Background-Dispatch, Split-Write, Self-Fallback, ISO-Woche-Fix, api-quirks-Reference
- ✅ Bootstrap-Symlink-Reset im Orchestrator-Prompt (statt Setup-Script, wegen Git-Klon-Timing)

**Offener Schritt:** Routine-Config-Sync in claude.ai (Abschnitt 0) + erster autonomer Run.

### Architektur-Verbesserungen

| Priority | Task | Begruendung |
|---|---|---|
| **P0** | **MCP-Endpoints absichern (aktuell offen fuer PoC).** Am 2026-04-18 wurde Bearer-Auth auf allen 9 n8n MCP Triggern + Mail-Bridge MCP deaktiviert, damit claude.ai Custom Connector UI sie anbinden kann (UI unterstuetzt keine statischen Authorization-Header). Konsequenz: URLs zu `https://n8n.srv867988.hstgr.cloud/mcp/*` sind oeffentlich zugaenglich — wer die URL kennt, kann MVV Google Ads Daten abfragen und Mails ueber den Gmail-Account senden. Nach erstem erfolgreichen Routine-Run (spaetestens 7 Tage) einen Auth-Layer einziehen. Favorisierter Pfad: Cloudflare Worker Proxy (Query-Param-Token, setzt dann Bearer an n8n). Alternativen: n8n Code-Node-Auth via `?token=`, oder Warten auf Header-Support im claude.ai-UI. | Kundendaten-Schutz |
| ~~P1~~ | ~~**Source-of-Truth-Konflikt Memory-Writer klaeren.**~~ **GEFIXT 2026-04-18** (commit `066e250`): Composer schreibt nur Report + MEMORY_UPDATE_PAYLOAD-JSON-Block, `scripts/memory_writer.py` macht alle 4 File-Updates. Harte Boundary im Composer-Prompt. | |
| ~~P1~~ | ~~**WoW-Vergleich funktional verifizieren.**~~ **GEFIXT 2026-04-18** (commit `066e250`): `data_quality.wow_verification` ist Pflicht-Feld im Performance-Analyst-Output mit beiden Timestamps + `both_successful`-Flag. Composer flagged WOW_UNVERIFIED falls fehlt. | |
| P2 | **GAQL-Query fuer Bundesland-Level-Geo (`user_location_view`) fixen.** In v1 und v2 hat der Call gefehlt (Sektion 6b nur Laender-Level). Muss in `performance-analyst.md` oder eigenem Skill ergaenzt werden. | Sektion 6b unvollstaendig |
| P2 | **Asset-Performance "PENDING" als "NO_DATA_AVAILABLE" statt leere Labels.** Google gibt einfach keine Ratings wenn Impressions < 5000. Composer sollte das explizit so melden statt leere Tabelle. | Report-Qualitaet |
| P3 | **Memory-Writer-Script mit besserem Dedup.** Aktuelle Regex-Logik matched manchmal zu grob (mehrspaltige Tabellen). Verbesserungs-Idee: Parse Markdown-Tabellen richtig, matche pro Zeile spezifisch die Term-Spalte. | `scripts/memory_writer.py` |

### Post-Smoke-Test Issues (KW16/2026-04-18 Cloud-Routine erster Run)

| Priority | Task | Begruendung |
|---|---|---|
| P1 | **Reporting-Workflow `geographic_performance` HTTP 400 bei Custom-Date-Range.** Der Query nutzt `WHERE segments.date DURING {{ $json.dateRange }}` — GAQL akzeptiert `DURING` aber nur mit Enum-Constants (LAST_7_DAYS etc.), NICHT mit Custom-Ranges wie `2026-04-11,2026-04-17`. Fuer Custom-Ranges muss der n8n-Workflow eine IF-Bedingung einbauen: wenn Enum -> `DURING`, wenn Custom -> `BETWEEN 'X' AND 'Y'`. Betrifft alle Reporting-Tools mit dateRange-Param (geographic, device, hourly, search_terms, budget_pacing, keyword, ad, campaign). **Workaround bereits dokumentiert** in `skills/weekly-report/references/api-quirks.md` QUIRK-1 (Agent nutzt GAQL-Fallback). Langfristfix im n8n-Workflow selbst. | Reporting-MCP Robustheit |
| ~~P1~~ | ~~**Sub-Agent Stream-Timeouts haerten.**~~ **TEILWEISE GEFIXT 2026-04-18** (commit `78f5e09`): Composer auf Background-Dispatch, Split-Write, Self-Fallback. Verbleibend: strictere Max-Duration-Boundaries in Sub-Agent-Briefings, DataForSEO in kleineren Chunks. Dokumentiert als QUIRK-7 in api-quirks.md. Re-evaluieren nach naechstem Run. | |
| ~~P2~~ | ~~**Statistician `LAST_90_DAYS`-Enum existiert nicht in Google Ads API.**~~ **GEFIXT 2026-04-18** (commit `0a2b915`) in `.claude/agents/statistician.md` — ab > 30 Tagen Custom-Range (`BETWEEN 'X' AND 'Y'`) statt Enum. Plus als QUIRK-2 in api-quirks.md. | |

### Session 2026-04-18 — neue Post-Smoke-Test-Items

| Priority | Task | Begruendung |
|---|---|---|
| P1 | **DataForSEO `keyword_suggestions` 128k-Token-Limit Risiko.** Tritt auf wenn bulk-Seeds gross. Workaround in QUIRK-4 dokumentiert (max 3 Seeds pro Call). Bei wiederkehrendem Problem: Sub-Agent-Scope in `.claude/agents/search-keyword-hunter.md` haerten (Whitelist-Pattern fuer search_volume). | Stream-Timeout-Risiko |
| P2 | **Alten Webhook-Mail-Bridge loeschen** (n8n-Workflow `sio56m2zxbOtSStz`). Wurde ersetzt durch MCP-Version `MWsWFnQubZ1Z21QL`. Nach erstem erfolgreichen Run mit MCP-Mail-Bridge safe zum Loeschen. | Cleanup |
| P2 | **`.mcp.json` Bearer-Token entfernen** (oder rotieren). Aktuell ist der Token `upkL5r84LOG...` noch in der lokalen `.mcp.json` — gitignored, aber wenn Fabian lokal entwickelt ohne Bearer-Auth in n8n, ist der Header im Call nutzlos. Cleanup: entweder Bearer in n8n reaktivieren und lokal via `.mcp.json` nutzen, oder Token aus `.mcp.json` raus und Authentication auf "none" setzen (konsistent mit Cloud-Setup). | Lokale Konsistenz |
| P3 | **Composer-Rendering weiter verfeinern**: Drei-Teile-Split statt zwei (Exec+Overview / Data / Recommendations) falls Stream-Timeouts trotz Split-Write auftreten. | Weitere Haerung |

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
