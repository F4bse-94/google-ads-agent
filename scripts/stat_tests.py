#!/usr/bin/env python3
"""Statistical tests for MVV Enamic Ads Weekly Report W16-2026."""

import math
import random
from scipy import stats

print("=" * 60)
print("H-default-1: Mobile CVR < Desktop CVR (90 days)")
print("=" * 60)

# Aggregated 90-day device data (all campaigns)
desktop_clicks = 563 + 837 + 62   # 1462
desktop_conv = 5 + 8.5 + 0        # 13.5
mobile_clicks = 233 + 292 + 102   # 627
mobile_conv = 0 + 0 + 0           # 0

print(f"Desktop: {desktop_clicks} clicks, {desktop_conv} conv, CVR = {desktop_conv/desktop_clicks*100:.3f}%")
print(f"Mobile:  {mobile_clicks} clicks, {mobile_conv} conv, CVR = {mobile_conv/mobile_clicks*100:.3f}%")

# Bayesian Beta-Binomial (Jeffreys prior Beta(0.5, 0.5))
alpha_d = 0.5 + 13.5   # 14
beta_d  = 0.5 + 1462 - 13.5  # 1449
alpha_m = 0.5 + 0       # 0.5
beta_m  = 0.5 + 627 - 0  # 627.5

random.seed(42)
n_sim = 200000
count_mobile_less = 0
desktop_samples = []
mobile_samples = []

for _ in range(n_sim):
    d = random.betavariate(alpha_d, beta_d)
    m = random.betavariate(alpha_m, beta_m)
    desktop_samples.append(d)
    mobile_samples.append(m)
    if m < d:
        count_mobile_less += 1

prob_mobile_less = count_mobile_less / n_sim
desktop_mean_post = alpha_d / (alpha_d + beta_d)
mobile_mean_post = alpha_m / (alpha_m + beta_m)

diffs_h1 = sorted([d - m for d, m in zip(desktop_samples, mobile_samples)])
ci_lower_h1 = diffs_h1[int(0.025 * n_sim)]
ci_upper_h1 = diffs_h1[int(0.975 * n_sim)]
mean_diff_h1 = sum(diffs_h1) / n_sim

cohens_h = 2 * (math.asin(math.sqrt(desktop_mean_post)) - math.asin(math.sqrt(mobile_mean_post)))

# Power analysis for frequentist Z-test equivalent
p1_est = desktop_mean_post
p2_est = mobile_mean_post
p_bar = (p1_est + p2_est) / 2
effect = abs(p1_est - p2_est)
z_alpha = stats.norm.ppf(1 - 0.05/2)
z_beta = stats.norm.ppf(0.80)
n_required_h1 = ((z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p1_est*(1-p1_est) + p2_est*(1-p2_est)))**2) / (effect**2)

print(f"\nBayesian posterior analysis:")
print(f"  P(Mobile CVR < Desktop CVR) = {prob_mobile_less:.4f}")
print(f"  Desktop posterior mean: {desktop_mean_post*100:.4f}%")
print(f"  Mobile posterior mean:  {mobile_mean_post*100:.4f}%")
print(f"  Diff (Desktop-Mobile):  mean={mean_diff_h1*100:.4f}%")
print(f"  95% HDI for diff:       [{ci_lower_h1*100:.4f}%, {ci_upper_h1*100:.4f}%]")
print(f"  Cohen s h:              {cohens_h:.4f}")
print(f"  Freq. n per group needed for 80% power: {int(math.ceil(n_required_h1))}")
print(f"  Current n: desktop={desktop_clicks}, mobile={mobile_clicks}")

print()
print("=" * 60)
print("H-default-2: CPA differs between PPA and Energiefonds (90 days)")
print("=" * 60)

ppa_total_conv = 8.5
ppa_cost_eur = (4614276464 + 841317262 + 94190000) / 1e6
ppa_cpa_overall = ppa_cost_eur / ppa_total_conv

ef_total_conv = 5.0
ef_cost_eur = (3298086913 + 691103345 + 217290000) / 1e6
ef_cpa_overall = ef_cost_eur / ef_total_conv

print(f"PPA: {ppa_total_conv} conv, EUR {ppa_cost_eur:.2f} cost, CPA = EUR {ppa_cpa_overall:.2f}")
print(f"EF:  {ef_total_conv} conv, EUR {ef_cost_eur:.2f} cost, CPA = EUR {ef_cpa_overall:.2f}")
print(f"Industriestrom: 0 conv -> excluded (CPA undefined)")

# Daily CPA values for days with conversions > 0
ppa_daily_cpa = [72.76, 28.04, 254.16, 79.76, 116.14, 71.64, 80.23, 81.47, 124.12]
ef_daily_cpa = [88.97, 67.19, 32.55, 131.98, 65.20]

ppa_mean_cpa = sum(ppa_daily_cpa) / len(ppa_daily_cpa)
ef_mean_cpa = sum(ef_daily_cpa) / len(ef_daily_cpa)
ppa_var = sum((x - ppa_mean_cpa)**2 for x in ppa_daily_cpa) / (len(ppa_daily_cpa) - 1)
ef_var = sum((x - ef_mean_cpa)**2 for x in ef_daily_cpa) / (len(ef_daily_cpa) - 1)
ppa_sd = math.sqrt(ppa_var)
ef_sd = math.sqrt(ef_var)

# Welch t-test
t_stat, p_value_h2 = stats.ttest_ind(ppa_daily_cpa, ef_daily_cpa, equal_var=False)

# Welch-Satterthwaite df
se_diff = math.sqrt(ppa_var/len(ppa_daily_cpa) + ef_var/len(ef_daily_cpa))
num = (ppa_var/len(ppa_daily_cpa) + ef_var/len(ef_daily_cpa))**2
den = ((ppa_var/len(ppa_daily_cpa))**2/(len(ppa_daily_cpa)-1) +
       (ef_var/len(ef_daily_cpa))**2/(len(ef_daily_cpa)-1))
df = num / den
t_crit = stats.t.ppf(0.975, df)
diff_mean_h2 = ppa_mean_cpa - ef_mean_cpa
ci_l_h2 = diff_mean_h2 - t_crit * se_diff
ci_u_h2 = diff_mean_h2 + t_crit * se_diff

# Cohen d
pooled_std = math.sqrt(((len(ppa_daily_cpa)-1)*ppa_var + (len(ef_daily_cpa)-1)*ef_var) /
                        (len(ppa_daily_cpa) + len(ef_daily_cpa) - 2))
cohens_d = diff_mean_h2 / pooled_std if pooled_std > 0 else 0

# Power
target_d = abs(cohens_d)
n_needed_h2 = ((stats.norm.ppf(0.975) + stats.norm.ppf(0.80))**2 * 2) / (target_d**2) if target_d > 0 else float("inf")

print(f"\nWelch t-test:")
print(f"  PPA mean CPA: EUR {ppa_mean_cpa:.2f} (sd={ppa_sd:.2f}, n={len(ppa_daily_cpa)})")
print(f"  EF  mean CPA: EUR {ef_mean_cpa:.2f} (sd={ef_sd:.2f}, n={len(ef_daily_cpa)})")
print(f"  t-statistic:  {t_stat:.4f}")
print(f"  p-value:      {p_value_h2:.4f}")
print(f"  df:           {df:.2f}")
print(f"  Diff (PPA-EF): EUR {diff_mean_h2:.2f}")
print(f"  95% CI:       [EUR {ci_l_h2:.2f}, EUR {ci_u_h2:.2f}]")
print(f"  Cohen s d:    {cohens_d:.4f}")
print(f"  n per group needed for 80% power: {int(math.ceil(n_needed_h2))}")

# Bootstrap supplementary
random.seed(123)
n_boot = 100000
boot_diffs_h2 = []
for _ in range(n_boot):
    ppa_s = [random.choice(ppa_daily_cpa) for _ in range(len(ppa_daily_cpa))]
    ef_s = [random.choice(ef_daily_cpa) for _ in range(len(ef_daily_cpa))]
    boot_diffs_h2.append(sum(ppa_s)/len(ppa_s) - sum(ef_s)/len(ef_s))

boot_diffs_h2.sort()
boot_ci_l = boot_diffs_h2[int(0.025 * n_boot)]
boot_ci_u = boot_diffs_h2[int(0.975 * n_boot)]
p_ppa_higher = sum(1 for d in boot_diffs_h2 if d > 0) / n_boot

print(f"\n  Bootstrap (100k):")
print(f"    P(PPA CPA > EF CPA) = {p_ppa_higher:.4f}")
print(f"    95% CI for diff: [EUR {boot_ci_l:.2f}, EUR {boot_ci_u:.2f}]")

print()
print("=" * 60)
print("H-default-3: Broad Match CVR < Phrase/Exact CVR")
print("=" * 60)
print("All active keywords with traffic use PHRASE match type.")
print("BROAD match: 0 clicks, 0 impressions in 90-day window.")
print("EXACT match: 0 clicks, 0 impressions in 90-day window.")
print("VERDICT: insufficient_data -- no comparison group exists.")

print()
print("=" * 60)
print("Multiple Testing Correction (Bonferroni)")
print("=" * 60)
alpha_corrected = 0.05 / 2
print(f"Testable hypotheses: 2 (H1, H2)")
print(f"Corrected alpha: {alpha_corrected}")
print(f"H2 p-value ({p_value_h2:.4f}) vs corrected alpha ({alpha_corrected}): ", end="")
print("SIGNIFICANT" if p_value_h2 < alpha_corrected else "NOT SIGNIFICANT")

print()
print("=" * 60)
print("FINAL VERDICTS")
print("=" * 60)
print(f"H-default-1: trend_only")
print(f"  -> 0 mobile conversions = data sparsity, not testable frequentist")
print(f"  -> Bayesian P(Mobile<Desktop) = {prob_mobile_less:.4f}")
print(f"H-default-2: insufficient_data")
print(f"  -> p={p_value_h2:.4f}, but n=9/5 conversion-days is severely underpowered")
print(f"  -> Need {int(math.ceil(n_needed_h2))} conv-days per group for 80% power")
print(f"H-default-3: insufficient_data")
print(f"  -> No Broad/Exact match traffic. Only PHRASE active.")
