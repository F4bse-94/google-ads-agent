# 03_Pending_Actions

Offene P0/P1-Recommendations aus den letzten Wochenreports. **Composer-managed:** Nach jedem Run erweitert um neue P0/P1-Items aus dem aktuellen Report (Sektion 11), aeltere Items wandern nach 4 Wochen ins Archiv-Block falls nicht erledigt.

**Workflow:**
- Erledigte Items mit `[x]` markieren (statt `[ ]`) — Composer erkennt das und laesst sie beim naechsten Run im Archiv-Block.
- Items koennen vorzeitig ins Archiv geschoben werden, indem die ganze Zeile manuell verschoben wird.
- Neue Items werden vom Composer NUR appendiert, nie geloescht oder umsortiert.

---

## Aktuelle Woche: _(wird vom Composer ab dem ersten Run gefuellt)_

### P0 — sofort
_(Empty)_

### P1 — diese Woche
_(Empty)_

---

## Vorwochen (1-4 Wochen alt)

_(Wird vom Composer rotiert.)_

---

## Archiv (>4 Wochen oder erledigt)

_(Wird vom Composer rotiert.)_
