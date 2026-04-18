# Decision Log — google-ads-agent

Wichtige Architektur- und Design-Entscheidungen, damit sie in 3 Monaten noch nachvollziehbar sind.

## Format

```
## YYYY-MM-DD: <kurze Entscheidungs-Ueberschrift>

**Kontext**: Was war die Ausgangslage?
**Entscheidung**: Was wurde entschieden?
**Begruendung**: Warum?
**Konsequenz**: Was heisst das fuer die Zukunft?
```

## Entscheidungen

---

## 2026-04-17: Architektur — Pure Anthropic-Stack (Option G)

**Kontext**: Fabian betreibt ein 4-Agenten-Google-Ads-System in Langdock. Diskutiert wurden 5 Alternativen: n8n-native, Claude Code-only, Claude Workspace-only, Hybrid n8n+Claude Code, und Pure Anthropic-Stack. Zwei Tatsachen entschieden:
- n8n v1.104.0 (21.07.2025) unterstuetzt HTTP Streamable Transport fuer MCP Server Trigger — das SSE-Problem mit Claude Workspace ist damit behebbar.
- Claude Code Routines (Research Preview ab 14.04.2026) bieten Cloud-basierte Scheduled Agents auf Anthropic-Infrastruktur.

**Entscheidung**: Pure Anthropic-Stack (Option G):
- Claude Code Routines (Cloud) = Weekly Report Scheduler
- n8n (self-hosted) = reines Tool-Backend (8 Google-Ads-MCPs + 1 DataForSEO-MCP)
- GitHub Repo = Memory-Backbone
- Claude Code lokal = Werkstatt zum Bau/Iterieren
- claude.ai Workspace = spaeter fuer Chat-Interface (Post-MVP)

**Begruendung**:
- Maximale Reasoning-Qualitaet (Opus/Sonnet voll nutzbar)
- Keine AI-Orchestrierung in n8n noetig (n8n glaenzt bei deterministischen Tool-Workflows, nicht bei Multi-Agent-Logik)
- Cloud-Scheduling ohne eigenes Hosting oder Dev-App
- Anthropic-native, konsistent, keine Hybrid-Pain
- 90% Performance-Gain laut Anthropic Multi-Agent Research Paper (Opus-Lead + Sonnet-Workers)

**Konsequenz**:
- n8n-Instanz muss auf ≥ v1.104.0 gebracht werden
- Claude Pro/Max/Team/Enterprise Plan noetig fuer Routines
- Memory-Koordination via File-Commits (nicht Message-Passing)
- Fallback auf Hybrid (Option E) falls Claude-Workspace-MCP mit 8 Connectors instabil wird

---

## 2026-04-17: Memory — Neuer Repo `google-ads-memory`

**Kontext**: Langdock-System nutzt Repo `F4bse-94/langdock-ads-memory` mit 4 Markdown-Files. Optionen waren: Fork, parallel schreiben, oder neu anlegen.

**Entscheidung**: Neuer GitHub-Repo `google-ads-memory`. Strategy-Manifest-Inhalte werden manuell uebernommen, Rest faengt frisch an. Langdock-System bleibt unberuehrt parallel laufen.

**Begruendung**:
- Saubere Schema-Kontrolle: neue Files (z.B. `02_findings_log.md` mit Hypothesen-Status) nicht in altem Repo stoerend
- Keine Schema-Drift zwischen Welten
- Langdock-System kann als Fallback weiterlaufen ohne Konflikt

**Konsequenz**:
- Neuer GitHub-Repo anzulegen (Phase 3)
- Migrations-Schritt fuer Strategy-Manifest dokumentieren
- Zwei parallele Memory-Systeme — Doppelpflege falls beide aktiv bleiben. Nach erfolgreichem MVP-Run entscheiden ob Langdock-System abgeschaltet wird.

---

## 2026-04-17: DataForSEO — im MVP mitbauen

**Kontext**: Option war DataForSEO erst Phase 8 oder schon im MVP.

**Entscheidung**: Im MVP, Phase 2. Neuer n8n-Workflow `09-dataforseo-mcp.json` (Hub-and-Spoke wie die anderen) mit Tools: `keyword_overview`, `keyword_suggestions`, `search_volume`, `related_keywords`, `competitors_domain`, `domain_overview`, `ranked_keywords`, `serp_search`.

**Begruendung**:
- Market & Competitive Agent ist sinnvoll von Tag 1 — ohne Marktblick blinder Flug
- Report-Sektion 9 ("Market & Competitive") bleibt sonst leer bis Phase 8
- Einmaliger Aufwand Hub-and-Spoke-Workflow — kein Mehraufwand in spaeteren Phasen

**Konsequenz**:
- API-Quota DataForSEO pruefen (Kosten ~50-100 USD/Monat fuer unseren Scope)
- Credentials in n8n einrichten
- Phase 2 dauert laenger (2 Sessions statt 1)

---

## 2026-04-17: Email-Delivery — Gmail via MCP-Connector

**Kontext**: Optionen waren Gmail-Connector, n8n-Email-Workflow, Slack, oder alle drei.

**Entscheidung**: Gmail-Connector in claude.ai. Report-Composer ruft Gmail-MCP-Tool `send_email` auf. Empfaenger: Fabian, der per Forward an Agentur weiterleitet.

**Begruendung**:
- Einfachste Loesung, null Extra-Workflow
- Gmail-Connector wird von Claude Workspace + Routines nativ unterstuetzt
- Fabian's Workflow (Forward an Agentur) bleibt erhalten

**Konsequenz**:
- Gmail-Connector muss in claude.ai unter Settings > Connectors aktiviert werden
- Report-Composer-Prompt enthaelt konkrete Email-Formatierungsanweisung (Subject, Body, Anhang-Verweis auf GitHub)

---

## 2026-04-17: Sub-Agents — Claude Code Sub-Agent-Format

**Kontext**: Optionen waren native Claude-Code-Sub-Agents (`.claude/agents/*.md` mit YAML-Frontmatter, auto-dispatched via Task-Tool) ODER Routine-interner Dispatch via Task-Tool aus einem Haupt-Prompt.

**Entscheidung**: Native Claude-Code-Sub-Agents. Jeder Sub-Agent = eigenes Markdown-File in `.claude/agents/` mit Frontmatter (name, description, tools, model).

**Begruendung**:
- Anthropic-Standard-Pattern (Agent Teams)
- Parallel-Dispatch wird von Claude Code automatisch gehandhabt
- Klare Trennung: Sub-Agent-Prompts sind eigene Files, nicht im Orchestrator-Prompt vergraben
- Testbar einzeln (lokaler Claude Code kann gezielt einen Sub-Agent triggern)

**Konsequenz**:
- `.claude/` muss im Subprojekt angelegt werden (Abweichung vom n8n-projects-Default)
- 6 Sub-Agent-Markdown-Files zu schreiben in Phase 4
- Orchestrator-Prompt verweist explizit auf Sub-Agent-Namen

---

## 2026-04-17: Bearer-Auth auf allen 9 MCP-Triggern

**Kontext**: Nach Phase-2-Backup festgestellt: alle 9 MCP-Trigger hatten `authentication: none`. Die Endpoints waren damit public — wer den Path kannte (per URL-Struktur leicht erratbar), konnte Tools ausfuehren, inklusive Write-Operationen auf dem Google Ads Account.

**Entscheidung**: Einheitliche Bearer-Auth fuer alle 9 Workflows via einem gemeinsamen Credential.
- Credential-Name: `Google Ads Agent MCP Bearer` (Typ `httpBearerAuth`)
- Credential-ID in n8n: `idC1kOT9LEzjFFJe`
- Ein Token fuer alle 9 (nicht 9 separate)

**Begruendung**:
- Ein Token ist pragmatisch: Claude Code / Routine braucht nur eine ENV-Var
- Gleiches Credential fuer alle MCP-Server vereinfacht Rotation
- n8n Public API unterstuetzt `POST /credentials` mit `httpBearerAuth`-Typ → komplette Automatisierung moeglich
- `n8n_update_partial_workflow` (MCP-Tool) erlaubt das Setzen von `parameters.authentication` und `credentials.httpBearerAuth` in einer Operation pro Workflow

**Konsequenz**:
- Token liegt in `google-ads-agent/.mcp.json` (gitignored, darf lokal im Klartext)
- In Claude Code Routine muss der Token als ENV-Variable hinterlegt werden (nicht hardcoded im Prompt)
- Bei Token-Rotation: Credential in n8n updaten (UI oder `PUT /api/v1/credentials/:id`) + `.mcp.json` + Routine-ENV-Var
- Kompromittierung eines Tokens betrifft alle 9 MCPs → Rotation-Prozess muss dokumentiert sein (ist in `docs/workflow-atlas.md`)

---

## 2026-04-17: Modell-Profil (Default)

**Kontext**: Modellwahl je Agent. Kosten vs. Qualitaet-Trade-off.

**Entscheidung**:
- Orchestrator = Opus 4.7 (Reasoning-Tiefe fuer Delegation)
- Performance-Analyst = Sonnet 4.6
- Search-Keyword-Hunter = Sonnet 4.6
- Statistiker = Opus 4.7 (Reasoning-Tiefe fuer stat. Validierung, Hypothesen-Konstruktion)
- Market & Competitive = Sonnet 4.6
- Report-Composer = Sonnet 4.6 (Template-Rendering)

**Begruendung**:
- Anthropic Multi-Agent Research: Opus-Lead + Sonnet-Workers = beste Cost/Quality-Ratio
- Statistiker braucht Opus weil Reasoning-intensive Hypothesen-Bildung und Test-Auswahl
- Composer braucht kein Opus — strikte Template-Befolgung

**Konsequenz**:
- Nach 2-3 Test-Runs evaluieren: reicht Sonnet auch fuer Orchestrator oder Statistiker?
- Kosten-Monitoring in Phase 7
