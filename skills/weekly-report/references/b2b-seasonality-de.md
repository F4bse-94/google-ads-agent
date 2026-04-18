# B2B-Saisonalitaet Deutschland — MVV-Kontext

Referenz fuer Wochentag-, Monats- und Jahres-Patterns, die bei Anomalie-Detection und WoW-Vergleichen beruecksichtigt werden muessen.

## Wochentag-Pattern (kritisch!)

MVV-Traffic ist klar B2B-dominiert. Verteilung:

| Wochentag | Traffic-Anteil (grob) | CVR-Niveau | Bemerkung |
|---|---|---|---|
| Montag | ~18% | mittel | Rebound nach Wochenende, viele Research-Clicks |
| Dienstag | ~20% | hoch | Peak-Tag fuer B2B-Lead-Gen |
| Mittwoch | ~20% | hoch | Peak-Tag |
| Donnerstag | ~18% | mittel-hoch | stabil |
| Freitag | ~12% | mittel | Tail-Tag, viele abwesend ab Mittag |
| Samstag | ~6% | niedrig | Privatkunden-Noise dominiert |
| Sonntag | ~6% | niedrig | Ebenso |

**Implikation fuer Reporting:**
- WoW-Vergleiche **zwingend** wochentag-gematcht
- Anomalie-Detection: expected-Wert fuer Tag X ist Mittelwert der letzten 4 gleichen Wochentage
- Wochenende-Traffic separat betrachten: oft B2C-Noise, den Negative-Listen nicht 100% fangen

## Monats-Pattern

| Monat | Pattern | Kontext |
|---|---|---|
| Januar | Stark anziehend | Budget-Releases, Planung fuer Jahr |
| Februar-Maerz | Hoch | Q1-Aktivitaet, Jahresgespraeche |
| April-Juni | Hoch-stabil | Q2 Peak-Aktivitaet |
| Juli-August | Ruhig | Sommerpause, Einkaufsabteilungen unterbesetzt |
| September | Rebound | Q3-Aktivitaet, Messen-Kontext |
| Oktober-November | Hoch | Q4 Peak, Vertraege fuer naechstes Jahr |
| Dezember | Stark fallend | Weihnachten, Entscheider nicht erreichbar |

**Implikation:** MoM-Vergleiche nur mit Saisonalitaets-Korrektur (YoY-Vergleich verlaesslicher).

## Jahres-Events (Energie-spezifisch)

| Event | Zeitraum | Ads-Impact |
|---|---|---|
| E-world (Messe Essen) | Februar | Traffic-Peak, Brand-Awareness steigt 2-4 Wochen davor |
| Jahreswechsel Stromvertraege | Oktober-Dezember | Peak-CVR fuer Commodity |
| Strompreis-Ankuendigungen | variabel | Traffic-Spikes bei politischen Preiserhoehungen |
| Heizperiode-Start | September-Oktober | Energie-Themen generell relevanter |

## Feiertage (DE)

| Feiertag | Datum (2026) | Anmerkung |
|---|---|---|
| Neujahr | 01.01. | Kein Business-Traffic |
| Karfreitag | 03.04. | Brueckentag-Kontext |
| Ostermontag | 06.04. | Brueckentag-Kontext |
| Tag der Arbeit | 01.05. | Kein Business |
| Christi Himmelfahrt | 14.05. | Brueckentag, Do + Fr oft ruhig |
| Pfingstmontag | 25.05. | — |
| Fronleichnam (nur BW, BY, NW, RP, SL, SN, TH) | 04.06. | Regionale Wirkung |
| Tag der Deutschen Einheit | 03.10. | Kein Business |
| Allerheiligen (katholische BL) | 01.11. | Regional |
| Weihnachten | 24.12.-26.12. | Kein Business |
| Silvester | 31.12. | Kein Business |

**Implikation:** Anomalie-Detection muss Feiertage rausfiltern oder als "expected low" kennzeichnen.

## Tageszeit-Pattern

Grober Verlauf eines B2B-Arbeitstages:

| Zeit | Aktivitaetslevel | Ads-Implikation |
|---|---|---|
| 00:00-06:00 | sehr niedrig | Privatkunden-Noise oder Retargeting |
| 06:00-08:00 | steigend | Fruehe Arbeitsanfaenge, Pendler lesen |
| 08:00-12:00 | Peak | Hauptarbeitszeit, Recherche-Clicks |
| 12:00-14:00 | Dip | Mittagspause |
| 14:00-17:00 | Peak | Zweite Haelfte, viele Entscheidungen |
| 17:00-20:00 | fallend | Feierabend, einzelne Klicks |
| 20:00-00:00 | niedrig | Hauptsaechlich B2C |

**Dayparting-Kandidat:** Kampagnen koennten theoretisch auf 08-18 Uhr beschraenkt werden. Aktuell nicht empfohlen (wuerde Recherche-Klicks abschneiden), aber in Hourly-Performance-Analyse immer mit reportieren.

## Annahmen fuer Anomaly-Detection

Wenn der Statistiker einen Tag als anomal flaggt:
1. Ist es ein Feiertag? → kein Anomalie-Flag
2. Ist es ein Wochenende? → anderes Vergleichs-Set (andere Wochenend-Tage der letzten Wochen)
3. Ist eine Brueckentag-Situation? → Toleranz erhoehen (Mittwoch zwischen 2 Feiertagen kann ungewoehnlich ruhig sein)
4. Ist es ein bekanntes Event? → annotieren in "kontextuelle Anomalie, nicht rein datengetrieben"

## Implementierungs-Hinweis

Wochentag-Korrektur-Pseudocode fuer Anomaly-Detection:
```python
from datetime import datetime
def is_anomaly(day_metric, historical_data, z_threshold=2.0):
    day = datetime.fromisoformat(day_metric['date'])
    weekday = day.weekday()  # 0 = Monday
    same_weekday_historical = [d['value'] for d in historical_data if datetime.fromisoformat(d['date']).weekday() == weekday]
    if len(same_weekday_historical) < 4:
        return ('insufficient_history', None)
    mean = np.mean(same_weekday_historical)
    std = np.std(same_weekday_historical)
    z = (day_metric['value'] - mean) / std if std > 0 else 0
    return ('anomaly' if abs(z) > z_threshold else 'normal', z)
```
