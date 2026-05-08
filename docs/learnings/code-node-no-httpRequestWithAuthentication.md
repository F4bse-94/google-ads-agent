# Code-Node hat kein `httpRequestWithAuthentication` — Helper-Webhook-Pattern

**Datum:** 2026-05-08
**Kontext:** KW19 Weekly-Report-Recovery — Memory-Bridge `hFLZBFb48I09iFdJ`, Node `Memory Atomic Edit`
**n8n-Version:** 2.35.1

## Symptom

Atomic-Edit-Code-Node wirft beim ersten Call:
```
The function "helpers.httpRequestWithAuthentication" is not supported in the Code Node [line 46]
```
5 von 5 Memory-Writes scheitern parallel, Report landet nicht in `google-ads-memory/reports/`.

## Root Cause

In n8n 2.35.1 (und allen Versionen <2.40.x) sind in Code-Nodes nur `$helpers.httpRequest()` (ohne Auth), `DateTime`, `$jmespath` verfuegbar. **Authentifizierte HTTP-Calls (`httpRequestWithAuthentication`) und Credential-Lookups (`getCredentials`) sind explizit gesperrt** — eine Sandboxing-Entscheidung, kein Bug.

Die Atomic-Edit-Refactor-Implementierung aus KW18-Post-Mortem (`github-edit-race-condition-atomic-pattern.md`) hat diese Helper-Funktion vorausgesetzt, ohne die Versions-Constraint zu pruefen.

## Loesung: Helper-Sub-Workflow mit Webhook

Code-Node delegiert authentifizierte Calls an einen separaten Workflow, der den `Predefined Credential Type`-Pfad des HTTP-Request-Nodes nutzt (dort funktionieren Credentials).

```
Memory Atomic Edit (Code-Node, Loop-Logik)
   │ POST http://localhost:5678/webhook/github-memory-helper
   ▼
GitHub Memory Helper (Workflow v4RObLQROoRe5Tb2)
   ├── Webhook (POST /github-memory-helper, responseMode=responseNode)
   ├── Switch on body.action  → get | put
   ├── HTTP Request (githubApi credential, fullResponse, neverError)
   └── Respond to Webhook  → { statusCode, body, headers }
```

Code-Node nutzt nur `$helpers.httpRequest()` (ohne Auth) gegen den Helper-Webhook. Helper macht Auth ueber die `githubApi`-Credential.

### Atomic-Pattern bleibt erhalten

- Loop, Backoff, 409/422-Retry, SHA-Roundtrip, create-vs-edit-Branching — alles im Code-Node, wie vorher
- Race-Condition-Schutz aus KW18 bleibt intakt
- Sub-Workflow sieht nur eine Action pro Call (`get` ODER `put`), keine Loop-Logik dort

## Critical Gotcha: NAT-Loopback / Localhost-URL

**Erste Implementierung mit der oeffentlichen URL `https://<your-n8n-host>/webhook/...` lief in 30s-Timeouts.**

Hostinger (und viele andere Self-Hosted-Setups hinter Reverse-Proxy / Cloudflare) erlauben Hairpin-NAT nicht — der n8n-Container kann seine eigene oeffentliche Hostname nicht aufloesen / erreichen. Self-HTTP-Calls haengen.

**Fix:** Localhost-URL `http://localhost:5678/webhook/<path>` im Code-Node. Das routet container-intern, ohne den Reverse-Proxy zu durchlaufen.

```js
const helperUrl = 'http://localhost:5678/webhook/github-memory-helper';
```

Externe Tester (curl von ausserhalb) muessen weiterhin die oeffentliche URL nutzen.

## Validation-Test

Helper-Webhook isoliert getestet via curl:
- GET 200 mit SHA → ✓
- GET 404 fuer nicht-existente Datei → ✓
- PUT 201 fuer Create (sha=null) → ✓
- PUT 200 fuer Update (mit sha) → ✓
- PUT 422 ohne sha bei existierender Datei → ✓ (triggert Retry-Loop)

End-to-End via Memory-Bridge → 1s pro Call, beide Pfade (created + edited) gruen.

## Vermeidung in Zukunft

1. Bei jedem `helpers.*Authentication`-Call im Code-Node: pruefen ob in installierter n8n-Version verfuegbar (siehe Skill `n8n-mcp-skills:n8n-code-javascript`, Abschnitt "Built-in Functions").
2. Bei n8n-self-Webhook-Calls IMMER `localhost:5678` statt public URL nutzen.
3. `validate_workflow` faengt das `httpRequestWithAuthentication`-Issue NICHT — es ist ein Laufzeit-Sandboxing-Problem, kein Schema-Fehler. Manueller Smoke-Test des Code-Nodes nach jedem Refactor noetig.

## Verwandte Files

- `workflows/10-memory-bridge.json` — Memory-Bridge mit gefixtem Code-Node
- `workflows/11-github-memory-helper.json` — Neuer Helper-Workflow
- `docs/learnings/github-edit-race-condition-atomic-pattern.md` — KW18-Post-Mortem mit dem urspruenglichen Atomic-Pattern
