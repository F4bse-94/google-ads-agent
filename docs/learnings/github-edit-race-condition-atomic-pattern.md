# GitHub-Edit Race-Condition in n8n — Atomic-Edit-Code-Node Pattern

**Datum:** 2026-05-08 | **Kontext:** KW18-Post-Mortem Memory Bridge

## Problem

Memory-Bridge-Workflow (`hFLZBFb48I09iFdJ`) feuerte beim Weekly-Report-Run 6 parallele GitHub-File-Updates ab (4 Memory-Files + Report + ggf. weitere). Pattern war: `GitHub Get Current SHA` → `GitHub Edit File` mit `retryOnFail: true, maxTries: 3`. **3 von 6 Updates failten** mit `409 Conflict` (`is at <sha-A> but expected <sha-B>`).

**Root Cause:** Klassische TOCTOU-Race. Zwischen SHA-Get und Edit committed ein paralleler Lauf seinen Edit → unser SHA ist stale → 409. Der `retryOnFail` retried mit dem ALTEN SHA aus dem GET-Node — daher hilft er nicht.

## Lösung: Atomic-Edit-Code-Node mit Re-Fetch

Ersetze die 3-Node-Kette (`Get-SHA`, `Edit-File`, `Create-File`) durch **einen Code-Node**, der GET+PUT in einer Schleife macht und bei 409 den SHA frisch holt. Bei 404 (file existiert nicht) → kein SHA in Body → GitHub create-Pfad.

```javascript
const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${filename.split('/').map(encodeURIComponent).join('/')}`;
const contentBase64 = Buffer.from(content, 'utf8').toString('base64');

for (let attempt = 1; attempt <= 5; attempt++) {
  let sha = null, exists = false;
  try {
    const r = await this.helpers.httpRequestWithAuthentication.call(this, 'githubApi',
      { method: 'GET', url: apiUrl, json: true });
    sha = r.sha; exists = true;
  } catch (e) {
    if ((e.httpCode || e.statusCode) === 404) exists = false;
    else throw e;
  }
  try {
    const body = { message: commitMessage, content: contentBase64 };
    if (exists) body.sha = sha;
    const r = await this.helpers.httpRequestWithAuthentication.call(this, 'githubApi',
      { method: 'PUT', url: apiUrl, body, json: true });
    return [{ json: { ok: true, attempt, action: exists ? 'edited' : 'created', ... } }];
  } catch (e) {
    const s = e.httpCode || e.statusCode;
    if ((s === 409 || s === 422) && attempt < 5) {
      await new Promise(r => setTimeout(r, 200 * Math.pow(2, attempt - 1) + Math.random() * 200));
      continue;
    }
    throw e;
  }
}
```

## Wichtig

- **Code-Node mit Credentials:** Im Node `credentials: { githubApi: { id, name } }` setzen — sonst kennt `httpRequestWithAuthentication` keine Auth.
- **Filename-Encoding:** `filename.split('/').map(encodeURIComponent).join('/')` — Slashes erhalten, andere Sonderzeichen escapen.
- **Backoff:** Exponential mit Jitter (`200 * 2^n + random`) verhindert Synchronized-Retry-Storms.

## Bestaetigt durch

Live-Test gegen das `google-ads-memory` Repo: Stale-SHA produziert reproduzierbar 409, Re-Fetch loest auf 200. Code-Node-Implementation ersetzt 3 alte Nodes; Workflow ist jetzt 9 statt 11 Nodes.

## Anwendbar auf

Jeden n8n-Workflow der parallel auf dieselbe GitHub-Datei schreibt. Insbesondere AI-Agent-getriggerte Sub-Workflows (mehrere Tool-Calls in einem Agent-Run).
