# Dokumentations-Standards

## CLAUDE.md

- **Top-Level CLAUDE.md**: Projekt-Zweck, Welten-Glossar, Arbeitsweise, globale Regeln
- **Sub-CLAUDE.md**: Pro Subprojekt, 40-80 Zeilen, spezifischer Kontext
- `@pfad/zu/datei.md` für gezielte Imports (max. 5 Hops)

## README.md

- Menschenlesbar
- Einstiegspunkt für andere und Fabian nach längerer Pause
- Ordner-Überblick, Setup, Links zu relevanten Docs

## DECISIONS.md (optional, pro Subprojekt wenn sinnvoll)

- Entscheidungs-Log: was wurde warum entschieden
- Verhindert dass in 3 Monaten niemand mehr weiss warum

## Learnings

- `docs/learnings/<slug>.md` — eine Datei pro Erkenntnis
- Frontmatter optional, aber Titel + Datum hilfreich
- Index in `docs/LEARNINGS.md` aktualisieren

## Plans & Specs

- `docs/plans/<datum>-<slug>.md` — Implementierungs-Plan mit Context, Struktur, Phasen, Risiken
- `docs/specs/<datum>-<slug>.md` — Design-Spezifikation eines Features

## Sessions

- `docs/sessions/<datum>-session-summary.md` nach wichtigen Arbeitstagen
- Nur wenn etwas Nicht-Offensichtliches in dieser Session gelernt/entschieden wurde
