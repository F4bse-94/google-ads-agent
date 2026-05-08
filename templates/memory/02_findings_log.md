# 02_Findings_Log

Persistente Liste aller **Hypothesen und statistischen Befunde** aus bisherigen Sessions. Kernstueck des Lern-Kreislaufs: offene Items (`insufficient_data`) werden vom Statistiker in spaeteren Sessions re-validiert, sobald mehr Daten vorliegen.

**Schreib-Regeln:**
- Composer (Memory-Bridge) appendet nach jedem Report
- Eintraege werden nicht geloescht, sondern mit neuem Status ueberschrieben
- Maximal 50 "offene" Eintraege — aeltere `confirmed`/`rejected` mit > 90 Tagen Alter wandern in Archiv-Sektion
- IDs sind fortlaufend (`F-001`, `F-002`, ...), damit Referenzen stabil bleiben

**Status-Werte:**
- `open` — Hypothese formuliert, noch nicht getestet
- `insufficient_data` — Test ausgefuehrt, Sample-Size zu klein fuer Aussage (Statistiker re-validiert in spaeteren Wochen)
- `significant_confirmed` — Test signifikant (p < 0.05 nach Multiple-Testing-Korrektur), Hypothese bestaetigt
- `significant_rejected` — Test signifikant in Gegenrichtung, Hypothese verworfen
- `not_significant` — Test ausgefuehrt, kein signifikanter Unterschied
- `trend_only` — Effekt-Richtung erkennbar, aber statistisch nicht signifikant

---

## Beispiel-Eintrag (Template — bei erstem Lauf entfernen oder ueberschreiben)

### F-000 — Beispiel-Hypothese: Mobile CVR < Desktop CVR

**Status:** open
**Erstellt:** `<KW/JAHR>`
**Letzte Pruefung:** _(noch nicht getestet)_
**Quelle:** Statistiker, Default-Hypothese H-default-1

**Hypothese:**
Mobile Conversion Rate ist signifikant niedriger als Desktop Conversion Rate.

**Test-Plan:** Z-Test fuer Proportionen (Mobile-CVR vs. Desktop-CVR) ueber LAST_14_DAYS.

**Verdict:** _(wird vom Statistiker beim ersten Run gefuellt)_

---

## Aktive Hypothesen

_(Wird vom Composer ab dem ersten Run gefuellt. Statistiker formuliert beim ersten Lauf 4 Default-Hypothesen — siehe `.claude/agents/statistician.md`.)_

---

## Archiv (>90 Tage, confirmed/rejected)

_(Wird vom Composer rotiert.)_
