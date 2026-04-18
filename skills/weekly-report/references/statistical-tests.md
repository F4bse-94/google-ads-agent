# Statistical Tests — Methodologie-Referenz

Nachschlagewerk fuer den Statistiker. Tests fuer typische Google-Ads-Fragestellungen, mit Entscheidungsregeln fuer Test-Auswahl, Annahmen-Check und Interpretation.

## Entscheidungsbaum Test-Auswahl

```
Was wird verglichen?
│
├── Anteil (CVR, CTR) zwischen 2 Gruppen
│   ├── n1, n2 >= 30 conv   → Two-Proportion Z-Test
│   └── n < 30              → Bayesian Beta-Binomial
│
├── Mittelwert (CPA, CPC) zwischen 2 Gruppen
│   ├── Varianzen gleich?    → Student's t-Test (selten zutreffend)
│   └── Varianzen ungleich   → Welch's t-Test (Default!)
│
├── Trend ueber 3+ Zeitpunkte
│   ├── Anteile              → Cochran-Armitage Chi-sq
│   └── Mittelwerte          → Linear-Regression mit t-Test auf Steigung
│
├── Unabhaengigkeit von 2 kategoriale Variablen
│   └──                       → Chi-sq Test of Independence
│
└── Zeit-Reihen-Anomalie (Wochentag-korrigiert)
    └──                       → Z-Score ueber rolling-mean (letzte 4 gleiche Wochentage)
```

## Tests im Detail

### 1. Two-Proportion Z-Test

**Frage:** "Ist CVR Gruppe A signifikant unterschiedlich zu CVR Gruppe B?"

**Formel:**
```
pooled_p = (x1 + x2) / (n1 + n2)
se = sqrt(pooled_p * (1 - pooled_p) * (1/n1 + 1/n2))
z = (p1 - p2) / se
p_value = 2 * (1 - Phi(|z|))   # two-sided
ci_95 = (p1 - p2) ± 1.96 * sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
```

**Annahmen:**
- n1 * p1, n1 * (1-p1), n2 * p2, n2 * (1-p2) alle >= 5 (besser >= 10)
- Unabhaengige Stichproben

**Python-Implementierung:** `scipy.stats.proportions_ztest`

### 2. Welch's t-Test

**Frage:** "Unterscheidet sich die mittlere CPA signifikant zwischen Kampagne A und B?"

**Formel:**
```
t = (mean1 - mean2) / sqrt(var1/n1 + var2/n2)
df = (var1/n1 + var2/n2)^2 / ((var1/n1)^2/(n1-1) + (var2/n2)^2/(n2-1))  # Welch-Satterthwaite
p_value = 2 * (1 - CDF_t(|t|, df))
ci_95 = (mean1 - mean2) ± t_crit(0.025, df) * sqrt(var1/n1 + var2/n2)
```

**Annahmen:**
- Daten sind unabhaengig und etwa normalverteilt (bei n > 30 tolerant)
- Varianzen DUERFEN ungleich sein (Grund fuer Welch)

**Wann statt Student's t:** Immer, ausser die Varianzen sind provably gleich (selten bei Ads-Daten).

**Python:** `scipy.stats.ttest_ind(x1, x2, equal_var=False)`

### 3. Bayesian Beta-Binomial (fuer kleine Samples)

**Frage:** "Bei n < 30 Conversions — was ist die Posterior-Verteilung der CVR?"

**Prior:** Beta(1, 1) (uninformative) oder Beta(alpha, beta) aus historischen Daten.

**Posterior nach Beobachtung (x Conversions, n-x keine):**
```
alpha_post = alpha_prior + x
beta_post = beta_prior + (n - x)
mean_post = alpha_post / (alpha_post + beta_post)
ci_95 = scipy.stats.beta.ppf([0.025, 0.975], alpha_post, beta_post)
```

**Vorteil:** funktioniert auch bei n = 1, 2, 3. Frequentist wird bei kleinen n instabil.

### 4. Cochran-Armitage Trend Test

**Frage:** "Gibt es einen konsistenten Trend in CVR ueber 3+ Zeitpunkte?"

**Input:** Mehrere (Anteil, Sample-Size)-Paare, zeitlich geordnet.

**Formel:**
```
T = Sum_i( t_i * (x_i - n_i * pbar) ) / sqrt(pbar * (1-pbar) * Sum_i( n_i * (t_i - tbar)^2 ))
p_value = 2 * (1 - Phi(|T|))
```

wobei `t_i` der Zeitpunkt (1, 2, 3, ...), `pbar` die ueberall-gepoolte Proportion.

**Anwendung MVV:** Statistiker testet ueber 4+ Wochen ob z.B. CVR kontinuierlich sinkt.

**Python:** `statsmodels.stats.contingency_tables.cochrans_q` (fuer Reihen-Dichotomie) oder eigene Implementierung.

### 5. Bonferroni Multiple Testing Correction

**Wann anwenden:** 3+ Hypothesen im selben Run.

**Anwendung:**
```
alpha_corrected = 0.05 / n_tests
```

Jeder individuelle Test verwendet `alpha_corrected` statt 0.05.

**Konservativ:** Bonferroni ist zu konservativ bei >10 Tests → dann FDR nutzen.

### 6. Benjamini-Hochberg FDR

**Wann:** 10+ parallele Tests.

**Prozedur:**
1. Sortiere p-Werte aufsteigend: p_(1) ≤ p_(2) ≤ ... ≤ p_(m)
2. Finde groesstes k so dass p_(k) ≤ k/m * alpha
3. Alle Hypothesen mit p_(i) ≤ p_(k) werden abgelehnt

**Python:** `statsmodels.stats.multitest.multipletests(pvals, method='fdr_bh')`

### 7. Z-Score-Anomalie (Wochentag-korrigiert)

**Frage:** "Ist die Conv-Rate heute auffaellig?"

**Prozedur:**
1. Wochentag des heutigen Tages bestimmen (z.B. Mittwoch)
2. Historische Conv-Rate der letzten 4 gleichen Wochentage sammeln
3. `mean_historic, std_historic = mean(hist), std(hist)`
4. `z_today = (cvr_today - mean_historic) / std_historic`
5. Flag bei `|z| > 2` (95% Konfidenz) oder `|z| > 3` (99% Konfidenz)

**Kritisch fuer MVV:** Ohne Wochentag-Korrektur kommt es zu Fehlalarmen, weil Mo-Fr und Sa-So stark unterschiedlich sind.

## Power Analysis

**Fuer Two-Proportion Z-Test:**

```python
# scipy: ausreichende Sample-Size fuer power=0.80
from statsmodels.stats.power import NormalIndPower
analysis = NormalIndPower()
n_required = analysis.solve_power(effect_size=0.2, alpha=0.05, power=0.80, alternative='two-sided')
```

**Fuer MVV (mit erwarteten p ~ 3-5%):** Detection of 1pp delta braucht ~3000-4000 Clicks pro Gruppe. Realistisch im Weekly-Report selten erreichbar bei Einzel-Keywords.

## Effect Size

Nicht nur p-Wert — immer Effect Size angeben.

### Fuer Proportionen: Cohen's h
```
h = 2 * arcsin(sqrt(p1)) - 2 * arcsin(sqrt(p2))
```
- |h| < 0.2: klein
- 0.2 ≤ |h| < 0.5: mittel
- |h| >= 0.5: gross

### Fuer Mittelwerte: Cohen's d
```
d = (mean1 - mean2) / pooled_sd
```
- |d| < 0.2: klein
- 0.2 ≤ |d| < 0.5: mittel
- 0.5 ≤ |d| < 0.8: gross
- |d| >= 0.8: sehr gross

## Confidence Intervals (Pflicht!)

Jede Aussage mit p-Wert MUSS ein 95%-KI haben. Begruendung: p-Wert zeigt NUR "signifikant oder nicht", KI zeigt die **Groesse** des Effekts.

Beispiel-Report-Zeile:
```
H1: Mobile CVR (2.1%) < Desktop CVR (3.8%) — Delta: -1.7pp [95% KI: -2.3pp, -1.1pp], p=0.003 — Verdict: significant_confirmed
```

## Interpretation-Regeln fuer Verdict

| p-Wert | Power | Verdict |
|---|---|---|
| < 0.05 AND power >= 0.80 | OK | `significant_confirmed` |
| < 0.05 AND power < 0.80 | borderline | `significant_confirmed` + Warning |
| 0.05 ≤ p < 0.10 | — | `trend_only` |
| >= 0.10 AND power >= 0.80 | — | `significant_rejected` |
| >= 0.10 AND power < 0.80 | — | `insufficient_data` |

## MVV-spezifische Hinweise

- **Sample-Sizes sind KLEIN** (Budget 3-4k EUR = ~50-100 conv/Monat)
- Bayesian ist oft realistischer als Frequentist
- Multiple-Testing-Korrektur ist PFLICHT weil Statistiker pro Run viele Tests macht
- Wochentag-Korrektur ist PFLICHT fuer B2B (siehe `b2b-seasonality-de.md`)
- Conversion-Lag: Letzte 7 Tage sind unterzaehlig — bei Tests Vorsicht

## Python-Dependencies (fuer GAQL-Analysen im Environment)

```
scipy >= 1.10
statsmodels >= 0.14
numpy >= 1.24
```

(Im Claude Code Routine Environment via Setup-Script installierbar.)
