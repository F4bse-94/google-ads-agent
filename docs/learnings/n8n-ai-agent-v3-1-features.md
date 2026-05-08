# n8n AI Agent Node v3.1 — Fallback-LLM, Batch Processing, Streaming

**Datum:** 2026-05-08
**Kontext:** Diskussion ueber LLM-Fallback nach Azure-Quota-429-Issues. User hat Market-Intel-Workflow auf v3.1 upgegradet und gefragt, ob das Pattern auf alle Sub-Agents ausgerollt werden soll.

## Major-Version-Sprung: v1.x → v3.1

Die meisten unserer Sub-Agent-Workflows nutzen `@n8n/n8n-nodes-langchain.agent` typeVersion **1.7**. Inzwischen ist v3.1 verfuegbar mit kritischen neuen Features.

### Breaking Change v1.x → v3.x

> Prior to version 1.82.0, the AI Agent had a setting for working as different agent types. This has now been removed and all AI Agent nodes work as a Tools Agent.

Da unsere Sub-Agents alle den `Tools Agent`-Pattern nutzen (`toolWorkflow`-Sub-Nodes), ist die Migration **safe**. Keine Code-Aenderung noetig, nur typeVersion bump + neue Properties.

## Neue Features in v3.1 (relevant)

### 1. `needsFallback: boolean` + zweite ai_languageModel-Connection

**Das ist der Game-Changer fuer Rate-Limit-Resilienz.**

Wenn primary LLM fail (429, timeout, API-error), schaltet n8n automatisch auf einen zweiten LLM-Node — keine manuelle Branch-Logik noetig.

**Setup:**
1. Im Agent-Node Property `Enable Fallback Model` aktivieren (`needsFallback: true`)
2. Auf der Canvas eine ZWEITE LLM-Node (z.B. `lmChatAzureOpenAi` mit Mini-Model) anlegen
3. Beide LLM-Nodes mit dem Agent-Node verbinden — n8n erkennt automatisch die zweite als Fallback

**Vorteil ggu. eigener Branch-Architektur:**
- Kein doppelter Agent-Node mit IF/Switch
- Tool-Connections, System-Message, etc. werden NICHT dupliziert
- Auto-Retry-Logik im Hintergrund

### 2. Batch Processing (`options.batching`)

Built-in Rate-Limiting fuer Tool-Aufrufe:

```json
{
  "options": {
    "batching": {
      "batchSize": 1,
      "delayBetweenBatches": 2000
    }
  }
}
```

`batchSize=1, delayBetweenBatches=2000ms` = effektiv 1 Tool-Call pro 2 Sekunden. Hilft bei DataForSEO und anderen Tools mit strikten Rate-Limits.

Im Vergleich: v1.x hatte das nicht — Tool-Aufrufe gingen so schnell wie der Agent sie planen konnte.

### 3. `enableStreaming: boolean` (default true in v3.1)

Streaming der Response — bei langen Outputs (z.B. Composer der 12-Sektionen-Markdown rendert) sieht man Tokens fliessen statt 60s warten.

Fuer single-shot Sub-Agents (Performance, Market, etc.) ist Streaming weniger relevant — das End-Output-JSON braucht der nachgelagerte Workflow als Ganzes. Kann optional auf `false` gesetzt werden.

### 4. `maxIterations` (default 10)

Hard-cap auf Tool-Aufruf-Zyklen. Wir haben in Prompts `MAX 15 Tool-Calls total` definiert — der `maxIterations`-Default 10 ist STRENGER. Wenn ein Sub-Agent mehr als 10 Tool-Aufrufe braucht, Property auf 15 oder 20 setzen.

### 5. `returnIntermediateSteps: boolean` (default false)

Wenn `true`: Output enthaelt nicht nur das finale JSON sondern auch alle Tool-Call-Zwischenschritte. Nuetzlich fuer **Debugging**, aber blaeht den Output stark auf.

### 6. `passthroughBinaryImages: boolean` (default true)

Fuer multimodal-use-cases — bei uns nicht relevant, alle Sub-Agents arbeiten textuell.

## Was sich NICHT geaendert hat

- System-Message lebt weiterhin in `parameters.options.systemMessage`
- Prompt-Source: `promptType` mit Optionen `auto` (Chat-Trigger) oder `define` (custom)
- Tool-Connections via `ai_tool` ports — gleicher Mechanismus
- Memory-Connection via `ai_memory` port — gleicher Mechanismus

## Memory-Frage

**Brauchen Sub-Agents eine Memory-Connection?** Klare Antwort: **Nein.**

Memory-Nodes (`memoryBufferWindow`, `memoryBuffer`, `memoryRedis`, etc.) speichern Multi-Turn-Conversation-State. Sie sind nuetzlich fuer:
- Chat-Trigger-Workflows mit fortlaufendem Dialog (z.B. unser Orchestrator-Chat-Mode hat `Chat Buffer Memory`)
- Long-running interactive Sessions
- Workflows wo der Agent ueber mehrere Aufrufe hinweg State braucht

Unsere Sub-Agents werden vom Orchestrator **single-shot** aufgerufen mit einem JSON-Briefing, machen ihren Job und geben JSON zurueck. Kein State zwischen den Aufrufen noetig — Memory-Connection waere reiner Overhead und potenzielle Halluzinations-Quelle (alte Daten aus dem Buffer).

Ausnahmen:
- **Orchestrator (Chat-Mode)**: Hat bereits `Chat Buffer Memory` ✓ — das ist korrekt, der User soll Folgefragen stellen koennen
- **Statistician**: Liest `02_findings_log.md` als "persistente Memory" via read_memory_file Tool — das ist semantisch besser als Buffer-Memory, weil es echte Hypothesen-Continuity ueber Wochen ermoeglicht

## Migration v1.7 → v3.1 — Vorgehen

Schritte pro Workflow:
1. Im n8n-UI: Agent-Node anklicken → "..." → "Replace with new version" → Version 3.1 auswählen
2. Properties pruefen — der `Tools Agent`-Mode wird automatisch uebernommen
3. `Enable Fallback Model` auf true setzen
4. Auf Canvas eine zweite LLM-Node anlegen (z.B. `lmChatAzureOpenAi` mit gpt-5.4-mini), mit dem Agent verbinden
5. Optional: `Batch Processing` mit `batchSize=1, delayBetweenBatches=2000` setzen, falls Tool-Rate-Limit problematisch
6. Test-Run

**Achtung:** Via n8n MCP-API direkt updaten ist riskant — eine `typeVersion`-Aenderung bricht ggf. Property-Schema. **Im UI machen** ist sicherer.

## Verbessertes Setup fuer unsere 5 Sub-Agents

| Workflow | Primary | Fallback | Batch | Begruendung |
|---|---|---|---|---|
| Performance-Analyst | gpt-5.4 | gpt-5.4-mini | nein | Tool-Discipline kritisch (QS-GAQL-Pflicht) — Fallback wichtig |
| Search-Keyword-Hunter | gpt-5.4-mini | gpt-5.4-mini | nein | Bereits Mini, Fallback als Sicherung |
| Statistician | gpt-5.4-mini | gpt-5.4-mini | nein | Aktuell Mini, Fallback als Sicherung |
| Market-Intelligence | gpt-5.4 | gpt-5.4-mini ✓ | optional | Bereits umgestellt durch User |
| Composer | gpt-5.4-mini | gpt-5.4-mini | nein | Rendering-Task, Fallback als Sicherung |
| Orchestrator | gpt-5.4-mini | gpt-5.4-mini | nein | Hat bereits ChatBufferMemory; Fallback wichtig |

Memory-Buffer-Connections: NUR im Orchestrator-Chat-Mode. Kein Bedarf an weiteren Memory-Nodes.

## Beobachteter Failure-Mode: Mini-Orchestrator + Webhook-Trigger halluziniert

**Symptom:** Nach Upgrade des Orchestrator-Agents auf v3.1 mit `gpt-5.4-mini` als Primary-LLM zeigte ein TMP-Webhook-Trigger-Test-Run eine klare Halluzination:

- Orchestrator-Execution dauerte nur **2.5 Sekunden** (vs. ~3 Min bei einem echten Pipeline-Lauf)
- LLM-Call `executionTime: 2419ms` → genau EIN LLM-Roundtrip, KEIN Tool-Call-Loop
- Webhook-Response enthielt eine perfekt strukturierte Composer-JSON mit fake-SHAs (`d1e2f3a4b5c6d7e8f90123456789abcdeffedcba` — offensichtlicher Pattern-Hexstring)
- Der echte Report auf GitHub blieb unveraendert (kein Commit, keine Memory-Updates)
- `data_warnings` enthielt sich widersprechende Eintraege (z.B. `email_sent: true` plus `email-not-sent` warning)

**Diagnose:** `gpt-5.4-mini` ist zu schwach, um die Tool-Call-Sequenz aus dem System-Prompt korrekt zu planen. Statt dessen produziert es eine **plausibel aussehende One-Shot-JSON-Antwort** ohne ueberhaupt Tools aufzurufen. Bei v3.1 mit `enableStreaming: true` (default) verstaerkt sich das Verhalten — Mini liefert sehr schnell die "wahrscheinlichste" Antwort.

**Was funktioniert:** Sub-Agent-Workflows (mit `executeWorkflowTrigger`) laufen problemlos auf v3.1+Mini, weil sie konkrete kleinere Tool-Sequenzen ausfuehren. Composer auf v3.1+Mini macht echte Tool-Calls fuer Memory-Bridge.

**Was nicht funktioniert:** Orchestrator-Agent mit `gpt-5.4-mini` als Primary kann den 4-Worker-Dispatch + Composer-Ruf nicht zuverlaessig planen.

**Fix-Optionen:**

1. **Orchestrator auf `gpt-5.4` (Full) zurueckstellen** — Tool-Discipline kommt zurueck, aber 3 Full-LLMs parallel bei Schedule-Run (Orch + Perf + Market) → Quota-Druck. Akzeptabel mit Fallback-LLM bei 429.

2. **`enableStreaming: false`** im Orchestrator setzen — koennte das "schnelle Halluzination"-Verhalten reduzieren.

3. **Echte Schedule-Trigger statt Webhook-Trigger testen** — Schedule-Run am Mo 07:00 nutzt einen anderen Pfad in n8n (kein Webhook-Body als `$json` sondern Cron-getriggerte fixe Set-Node-Daten). Dieser Pfad hat in Run #1 (vor allen Refactors) regulaer 3 Minuten gedauert mit echten Tool-Calls.

**Empfehlung:** Vor finaler Bewertung den realen Mo-Schedule-Trigger abwarten. Wenn der auch halluziniert, Variante 1 (Orch auf Full).

## Verwandte Files

- `workflows/13-sub-market-intelligence.json` — bereits auf v3.1 mit Fallback (durch User-UI-Update)
- `workflows/12,14,15,16,17` — alle auf v3.1 mit Fallback per MCP-API upgegradet (Commit `d3...` 2026-05-08)
