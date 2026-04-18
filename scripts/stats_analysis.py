import math
import random

random.seed(42)
n_sim = 100000

# ============================================================
# F-001: DEVICE SPLIT (91 Tage: 2026-01-16 bis 2026-04-16)
# ============================================================

desktop_clicks = 564 + 840 + 62
desktop_conv = 5 + 8.5 + 0

mobile_clicks = 233 + 292 + 102
mobile_conv = 0

tablet_clicks = 39 + 19 + 1
tablet_conv = 0

desktop_cost = (3301756913 + 4592616464 + 313794951) / 1e6
mobile_cost = (691103345 + 831565926 + 468762689) / 1e6
tablet_cost = (220880000 + 94190000 + 4400000) / 1e6
total_cost = desktop_cost + mobile_cost + tablet_cost

print("=" * 60)
print("F-001: DEVICE SPLIT (91 Tage)")
print("=" * 60)
print(f"Desktop: {desktop_clicks} clicks, {desktop_conv} conv, CVR={desktop_conv/desktop_clicks*100:.2f}%, Cost={desktop_cost:.2f} EUR")
print(f"Mobile:  {mobile_clicks} clicks, {mobile_conv} conv, CVR=0.00%, Cost={mobile_cost:.2f} EUR")
print(f"Tablet:  {tablet_clicks} clicks, {tablet_conv} conv, CVR=0.00%, Cost={tablet_cost:.2f} EUR")
non_desktop_cost = mobile_cost + tablet_cost
print(f"Non-Desktop spend: {non_desktop_cost:.2f} EUR ({non_desktop_cost / total_cost * 100:.1f}%)")
print()

# Bayesian
alpha_prior = 0.5
beta_prior = 0.5

d_alpha = alpha_prior + desktop_conv
d_beta = beta_prior + (desktop_clicks - desktop_conv)
m_alpha = alpha_prior + mobile_conv
m_beta = beta_prior + (mobile_clicks - mobile_conv)

print(f"Desktop posterior: Beta({d_alpha:.1f}, {d_beta:.1f}), mean={d_alpha/(d_alpha+d_beta)*100:.3f}%")
print(f"Mobile posterior:  Beta({m_alpha:.1f}, {m_beta:.1f}), mean={m_alpha/(m_alpha+m_beta)*100:.3f}%")
print()

count_dh = 0
deltas = []
for _ in range(n_sim):
    d_s = random.betavariate(d_alpha, d_beta)
    m_s = random.betavariate(m_alpha, m_beta)
    if d_s > m_s:
        count_dh += 1
    deltas.append(d_s - m_s)

prob_h1_f001 = count_dh / n_sim
deltas.sort()
ci_low = deltas[int(0.025 * n_sim)]
ci_high = deltas[int(0.975 * n_sim)]
mean_delta = sum(deltas) / len(deltas)

print(f"P(Desktop CVR > Mobile CVR) = {prob_h1_f001*100:.2f}%")
print(f"Delta (Desktop-Mobile): mean={mean_delta*100:.3f}pp, 95% CI=[{ci_low*100:.3f}pp, {ci_high*100:.3f}pp]")

p1 = desktop_conv / desktop_clicks
p2_eps = 0.001
h = 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2_eps))
print(f"Cohens h: {h:.3f}")

z_a = 1.96
z_b = 0.84
p_d = desktop_conv / desktop_clicks
p_m = 0.005
n_req_f001 = ((z_a + z_b)**2 * (p_d*(1-p_d) + p_m*(1-p_m))) / (p_d - p_m)**2
print(f"Power: need {math.ceil(n_req_f001)} mobile clicks (have {mobile_clicks}, gap {math.ceil(n_req_f001)-mobile_clicks})")
print()

# ============================================================
# F-003: DATA GAP
# ============================================================
print("=" * 60)
print("F-003: DATA GAP ANALYSIS")
print("=" * 60)

pre_ppa = (53775290 + 29010000 + 5020000 + 97400292 + 85130000) / 1e6
pre_ef = (32209219 + 5610000 + 9100000 + 79982666 + 34790000) / 1e6
pre_ind = (36055686 + 6932062 + 22830000 + 59980000 + 20070000) / 1e6
daily = (pre_ppa + pre_ef + pre_ind) / 5

print(f"Pre-gap daily avg: {daily:.2f} EUR/day")
print(f"Gap: 14 days (3/25 through 4/07)")
print(f"Estimated lost spend: {daily * 14:.2f} EUR")
print(f"  Energiefonds: PAUSED since 3/25 (23+ days, no resumption through 4/16)")
print(f"  PPA + Industriestrom: Gap 3/25 to 4/07, resumed 4/08")
print()

# ============================================================
# F-002: CPA COMPARISON
# ============================================================
print("=" * 60)
print("F-002: CPA COMPARISON")
print("=" * 60)

ppa_costs = [72762237, 28040000, 127080000, 79756574, 116140000, 71640000, 80231912, 81474453, 124124723]
ppa_convs = [1, 1, 0.5, 1, 1, 1, 1, 1, 1]
ppa_cpas = [c/1e6/cv for c, cv in zip(ppa_costs, ppa_convs)]

ef_costs = [88970000, 67190000, 32551513, 131980000, 65200311]
ef_convs = [1, 1, 1, 1, 1]
ef_cpas = [c/1e6/cv for c, cv in zip(ef_costs, ef_convs)]

n_p = len(ppa_cpas)
n_e = len(ef_cpas)
mp = sum(ppa_cpas)/n_p
me = sum(ef_cpas)/n_e
vp = sum((x-mp)**2 for x in ppa_cpas)/(n_p-1)
ve = sum((x-me)**2 for x in ef_cpas)/(n_e-1)

print(f"PPA: n={n_p}, mean CPA={mp:.2f}, sd={math.sqrt(vp):.2f}")
print(f"EF:  n={n_e}, mean CPA={me:.2f}, sd={math.sqrt(ve):.2f}")

se = math.sqrt(vp/n_p + ve/n_e)
t = (mp - me) / se
df_n = (vp/n_p + ve/n_e)**2
df_d = (vp/n_p)**2/(n_p-1) + (ve/n_e)**2/(n_e-1)
df = df_n / df_d

tc_table = {5:2.571, 6:2.447, 7:2.365, 8:2.306, 9:2.262, 10:2.228, 11:2.201, 12:2.179}
dfr = min(tc_table.keys(), key=lambda x: abs(x-df))
ci_l = (mp-me) - tc_table[dfr]*se
ci_h = (mp-me) + tc_table[dfr]*se

at = abs(t)
if at < 0.5:
    ps = "> 0.50"
elif at < 1.0:
    ps = "0.30-0.50"
elif at < 1.5:
    ps = "0.15-0.30"
elif at < 2.0:
    ps = "0.05-0.15"
else:
    ps = "< 0.05"

psd = math.sqrt(((n_p-1)*vp + (n_e-1)*ve)/(n_p+n_e-2))
cd = abs(mp-me)/psd
nr = 2*((1.96+0.84)/cd)**2

print(f"Welch t={t:.3f}, df={df:.1f}, p ~ {ps}")
print(f"Diff (PPA-EF): {mp-me:.2f} EUR, 95% CI=[{ci_l:.2f}, {ci_h:.2f}]")
print(f"Cohens d: {cd:.3f}, need n={math.ceil(nr)}/group for 80% power")
print()

# ============================================================
# H-default-3: WEEKDAY
# ============================================================
print("=" * 60)
print("H-default-3: WEEKDAY EFFECT")
print("=" * 60)

mf_c = (141+241+25)+(131+176+22)+(114+204+44)+(115+190+18)+(111+175+20)
mf_cv = (3+1.5+0)+(1+3+0)+(0+1+0)+(0+1+0)+(1+1+0)
ss_c = (98+71+14)+(126+94+22)
ss_cv = (0+0+0)+(0+1+0)

print(f"Mo-Fr: {mf_c} clicks, {mf_cv} conv, CVR={mf_cv/mf_c*100:.3f}%")
print(f"Sa-So: {ss_c} clicks, {ss_cv} conv, CVR={ss_cv/ss_c*100:.3f}%")

mfa = 0.5 + mf_cv
mfb = 0.5 + (mf_c - mf_cv)
ssa = 0.5 + ss_cv
ssb = 0.5 + (ss_c - ss_cv)

random.seed(42)
cmf = 0
dwd = []
for _ in range(n_sim):
    s1 = random.betavariate(mfa, mfb)
    s2 = random.betavariate(ssa, ssb)
    if s1 > s2:
        cmf += 1
    dwd.append(s1 - s2)

pmf = cmf/n_sim
dwd.sort()
wl = dwd[int(0.025*n_sim)]
wh = dwd[int(0.975*n_sim)]
wm = sum(dwd)/len(dwd)

print(f"P(Mo-Fr > Sa-So) = {pmf*100:.2f}%")
print(f"Delta: mean={wm*100:.3f}pp, 95% CI=[{wl*100:.3f}pp, {wh*100:.3f}pp]")
print()

# ============================================================
# H-default-4: HOURLY
# ============================================================
print("=" * 60)
print("H-default-4: HOURLY PEAK")
print("=" * 60)

ppa_hourly = {0:(1,0),3:(1,0),7:(3,0),8:(4,0),9:(8,0),10:(17,1),11:(10,0),12:(14,0),13:(6,0),14:(8,0),15:(6,0),16:(6,0),17:(1,0),18:(1,0),19:(1,0),20:(1,0),21:(1,0)}
ind_hourly = {4:(1,0),6:(2,0),7:(2,0),8:(1,0),9:(6,0),10:(4,0),11:(4,0),12:(2,0),13:(4,0),14:(5,0),15:(2,0),16:(1,0),17:(1,0),19:(3,0),20:(3,0),21:(1,0),22:(3,0),23:(1,0)}

ah = {}
for hd in [ppa_hourly, ind_hourly]:
    for hr,(c,cv) in hd.items():
        if hr not in ah:
            ah[hr]=[0,0]
        ah[hr][0]+=c
        ah[hr][1]+=cv

pk_c = sum(ah.get(h,[0,0])[0] for h in [9,10,11,12])
pk_cv = sum(ah.get(h,[0,0])[1] for h in [9,10,11,12])
rt_c = sum(v[0] for h,v in ah.items() if h not in [9,10,11,12])
rt_cv = sum(v[1] for h,v in ah.items() if h not in [9,10,11,12])
tc2 = pk_c + rt_c

print(f"Peak 09-12h: {pk_c} clicks ({pk_c/tc2*100:.1f}%), {pk_cv} conv")
print(f"Rest: {rt_c} clicks ({rt_c/tc2*100:.1f}%), {rt_cv} conv")

pka = 0.5+pk_cv
pkb = 0.5+(pk_c-pk_cv)
rta = 0.5+rt_cv
rtb = 0.5+(rt_c-rt_cv)

random.seed(42)
cpk = 0
for _ in range(n_sim):
    s1 = random.betavariate(pka, pkb)
    s2 = random.betavariate(rta, rtb)
    if s1 > s2:
        cpk += 1

ppk = cpk/n_sim
print(f"P(Peak > Rest) = {ppk*100:.2f}%")
print()

# ============================================================
# BONFERRONI
# ============================================================
print("=" * 60)
print("BONFERRONI CORRECTION")
print("=" * 60)
print("4 tests -> alpha_corrected = 0.0125 -> P(H1) threshold = 98.75%")
pf1 = "PASS" if prob_h1_f001 > 0.9875 else "FAIL"
pw = "PASS" if pmf > 0.9875 else "FAIL"
pp = "PASS" if ppk > 0.9875 else "FAIL"
print(f"F-001: {prob_h1_f001*100:.2f}% -> {pf1}")
print(f"F-002: p~{ps} -> FAIL")
print(f"H-def-3: {pmf*100:.2f}% -> {pw}")
print(f"H-def-4: {ppk*100:.2f}% -> {pp}")
