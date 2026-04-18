# Git-Konventionen

## Commit-Nachrichten

Stil: Conventional Commits.

```
<type>(<scope>): <summary>

<optional body>

<optional footer: Co-Authored-By, issue refs>
```

**Types**: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`.

## Branches

- Feature-Branch: `feat/<kurzer-slug>`
- Fix-Branch: `fix/<kurzer-slug>`
- Refactor: `refactor/<kurzer-slug>`
- Nie direkt auf `main` committen

## Vor jedem Commit

- `git status` prüfen — welche Dateien gehen rein?
- Keine Secrets committen (keys, tokens, credentials)
- `.mcp.json` ist gitignored — NICHT staging'en
- Pre-commit Hooks niemals mit `--no-verify` umgehen

## Push

- Force-Push nur auf eigene Feature-Branches, nie auf shared branches
- Nie `push --force` auf main
