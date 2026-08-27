#!/usr/bin/env python3
"""
build_shocks.py -- regenerate every GDyn policy shock file for
"Beyond Retaliation" from the GTAP 11 base tariff rates.

Reads  : data/BaseRate.har        (header RTMS) if HARPY is installed, else
         data/base_rates_RTMS.csv (shipped fallback, identical values)
         data/dsm_qxs_targets.csv (DSM bilateral export targets, Scenario 5)
Writes : Shocks/*.PSH        (GEMPACK/RunDynam policy shock files)

Every tms shock is computed with the power-of-the-tariff formula
    shock = 100 * [ (1 + t_new/100) / (1 + t_old/100) - 1 ]
because the GTAP variable tms is the percentage change in the POWER of the
tariff (1+t), not in the ad valorem rate t itself.

Run:  python build_shocks.py                       (uses the shipped CSVs)
      python build_shocks.py --har data/BaseRate.har  (uses your own database)
"""
import argparse, csv, os, re
import numpy as np
from harpy import HarFileObj

SEC = ["GrainCrop", "LiveMeat", "OthAgFood", "Coal", "Mining", "Metals", "Auto",
       "MachEquip", "ChemPlast", "TexApp", "OthManuf", "Utilities", "Construct",
       "TradeTran", "BusSvc", "PubOthSvc"]
REG = ["ZAF", "USA", "SACUSADC", "CHN", "EU27", "GBR", "ROW"]
MERCH = SEC[:11]                      # tariffs apply to merchandise only

# ---------------------------------------------------------------- parameters
# Share of each sector's exports to the USA exempted under Annex II of EO 14257.
# Source: authors' calculations from CEPII BACI; reproduced in Table 6.
EXEMPT_ZAF_USA = {"GrainCrop": 0.00, "LiveMeat": 0.00, "OthAgFood": 0.02,
                  "Coal": 1.00, "Mining": 0.87, "Metals": 0.50, "Auto": 0.00,
                  "MachEquip": 0.08, "ChemPlast": 0.20, "TexApp": 0.00,
                  "OthManuf": 0.05}
US_STATUTORY_ZAF = 30.0

# USA reciprocal tariff applied to third countries (additional percentage
# points on top of the existing MFN rate).  Energy and critical minerals
# (Coal, Mining) are exempt for every partner.
US_ON_THIRD = {"CHN": 30.0, "EU27": 15.0, "GBR": 10.0, "SACUSADC": 15.0, "ROW": 15.0}
US_THIRD_EXEMPT = {"Coal", "Mining"}

# Retaliatory tariff imposed BY each region ON USA goods, additional
# percentage points over the existing rate (Table 7).  Phased 2026-2027.
RETALIATION = {"CHN": 32.0, "EU27": 20.0, "GBR": 20.0,
               "ZAF": 10.0, "SACUSADC": 10.0, "ROW": 10.0}

# South African unilateral liberalisation: cut every applied rate to 50% of
# its initial level, in five equal steps of 10 percentage points of the
# initial rate per year, 2026-2030.
TARIFF_CUT_TOTAL = 0.50
CUT_YEARS = [2026, 2027, 2028, 2029, 2030]

# Real depreciation, delivered through the trade balance.
#
# DTBALR is an ORDINARY CHANGE variable and a FRACTION, not percentage points.
# From gdyn_v36s.tab:
#     100*INCOME(r)*DTBALR(r) = 100*DTBAL(r) - TBAL(r)*y(r)
# so DTBALR = [DTBAL - TBAL*y/100] / INCOME.  A value of 0.50 would mean a
# fifty percentage point of income swing in the trade balance.
#
# CALIBRATED from the Test D probe (POL2, DTBALR = 0.00916 for one year,
# measured against Scenario 1): realised depreciation 0.6173%, hence
#     DTBALR per 1% real depreciation = 0.01484
#
# Target: the minimum depreciation sufficient to offset the aggregate impact
# of the USA tariff shock.  Scenario 1 costs 0.478% of real exports, 0.200%
# of real GDP and US$803m of welfare; restoring each requires 0.069%, 0.044%
# and 0.051% respectively.  We target 0.1% cumulative over 2026-2030:
#     0.1 x 0.01484 = 0.001484 total  =>  0.00030 per year.
# Override at the command line, e.g.  --dtbalr 0.00297  (a 1% target)
DTBALR_PER_YEAR = 0.00030
DEP_YEARS = [2026, 2027, 2028, 2029, 2030]


def power_shock(t_old, t_new):
    """Percentage change in the power of the tariff, rates given in per cent."""
    return 100.0 * ((1.0 + t_new / 100.0) / (1.0 + t_old / 100.0) - 1.0)


def load_rtms(har_path, csv_path):
    """Base import tariff rates as (comm, source, dest), per cent.

    Prefers the HAR file so the rates come from your own aggregated database.
    Falls back to the shipped CSV if HARPY is not installed, so the package
    builds on a clean machine with no GEMPACK toolchain.
    """
    if har_path and os.path.exists(har_path):
        try:
            from harpy import HarFileObj
            arr = np.array(HarFileObj(har_path)["RTMS"].array)
            if arr.shape != (16, 7, 7):
                raise SystemExit(f"RTMS has shape {arr.shape}; expected (16,7,7). "
                                 "Is this the 16x7 aggregation?")
            print(f"Base tariff rates read from {har_path}")
            return arr
        except ImportError:
            print("HARPY not installed - falling back to the shipped CSV.")
    if not os.path.exists(csv_path):
        raise SystemExit(f"Neither {har_path} nor {csv_path} was found.")
    arr = np.zeros((16, 7, 7))
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            arr[SEC.index(row["sector"]),
                REG.index(row["source"]),
                REG.index(row["destination"])] = float(row["rate_pct"])
    print(f"Base tariff rates read from {csv_path}")
    return arr


def load_dsm(csv_path):
    """DSM bilateral export targets: {year: [(sector, dest, shock), ...]}."""
    if not os.path.exists(csv_path):
        raise SystemExit(f"{csv_path} not found - needed for Scenario 5.")
    out = {}
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            out.setdefault(int(row["year"]), []).append(
                (row["sector"], row["destination"], float(row["shock_pct"])))
    return out


def hdr(title, lines):
    bar = "!" + "=" * 70
    out = [bar, f"! {title}", bar]
    out += [f"! {l}" for l in lines]
    out += [bar, ""]
    return out


# ---------------------------------------------------------------- components
def us_tariff_on_zaf(rt):
    """Sector-specific USA tariff on South African goods (Table 6)."""
    L = hdr("USA reciprocal tariff on South African goods",
            ["Statutory rate 30%, scaled by the trade-weighted share of",
             "non-exempt products in each sector's exports to the USA.",
             "Reciprocal duties apply IN ADDITION to pre-existing rates,",
             "so the shock is an increment over the base rate.",
             "shock = 100 * [(1+t_new)/(1+t_old) - 1]"])
    zi, ui = REG.index("ZAF"), REG.index("USA")
    for s in MERCH:
        i = SEC.index(s)
        e = EXEMPT_ZAF_USA[s]
        d = US_STATUTORY_ZAF * (1.0 - e)
        t0 = rt[i, zi, ui]
        if d == 0.0:
            L.append(f'! shock tms("{s}","ZAF","USA") = 0; '
                     f'! fully exempt (base {t0:.3f}%)')
            continue
        L.append(f'shock tms("{s}","ZAF","USA") = {power_shock(t0, t0 + d):8.4f} ; '
                 f'! base {t0:6.3f}%, exempt {e:.0%}, +{d:.1f}pp')
    L.append("")
    return L


def us_tariff_on_third(rt):
    L = hdr("USA reciprocal tariff on third countries",
            ["Applied in addition to existing MFN rates.",
             "Energy products and critical minerals exempt for all partners."])
    ui = REG.index("USA")
    for r, d in US_ON_THIRD.items():
        ri = REG.index(r)
        L.append(f"! --- imports from {r}: +{d:.0f} percentage points")
        for s in MERCH:
            i = SEC.index(s)
            t0 = rt[i, ri, ui]
            if s in US_THIRD_EXEMPT:
                L.append(f'! shock tms("{s}","{r}","USA") = 0; ! exempt')
                continue
            L.append(f'shock tms("{s}","{r}","USA") = {power_shock(t0, t0 + d):8.4f} ; '
                     f'! base {t0:6.3f}%')
        L.append("")
    return L


def retaliation(rt, step, nsteps=2, exclude_zaf=False):
    """Retaliatory tariffs on USA goods, phased in `nsteps` equal power steps."""
    L = hdr(f"Retaliatory tariffs on USA goods -- phase {step} of {nsteps}",
            ["Additional percentage points over the existing applied rate",
             "(Table 7).  Phased in two equal steps across 2026-2027.",
             "Each step is an equal proportional change in the tariff power."])
    ui = REG.index("USA")
    for r, d in RETALIATION.items():
        if exclude_zaf and r == "ZAF":
            L.append("! --- ZAF on USA goods: netted into the tariff-cut block above")
            continue
        ri = REG.index(r)
        L.append(f"! --- {r} on USA goods: +{d:.0f}pp in total")
        for s in MERCH:
            i = SEC.index(s)
            t0 = rt[i, ui, ri]
            full = (1.0 + (t0 + d) / 100.0) / (1.0 + t0 / 100.0)
            per = 100.0 * (full ** (1.0 / nsteps) - 1.0)
            L.append(f'shock tms("{s}","USA","{r}") = {per:8.4f} ; ! base {t0:6.3f}%')
        L.append("")
    return L


def sa_import_tariffs(rt, k, with_retaliation):
    """Step k (1..5) of South Africa's import tariff path.

    Combines TWO policies that both act on tms(i, r, "ZAF"):
      - the unilateral cut of every applied rate to 50% of its initial level,
        in five equal annual steps;
      - in Scenarios 4 and 5 only, the 10 percentage point retaliatory tariff
        on USA goods, phased half in 2026 and half in 2027.

    They MUST be netted into one shock per component.  Emitting the cut and
    the retaliation as separate statements makes GEMPACK stop with
    "Some components of tms have been specified more than once".
    """
    n = len(CUT_YEARS)
    note = [f"Applied rates cut to {100*(1-TARIFF_CUT_TOTAL*k/n):.0f}% of their "
            f"initial level.",
            "'uniform -50' on tms is NOT equivalent to halving the tariff RATE:",
            "it halves the POWER (1+t), driving every rate to about -50%, i.e.",
            "an import subsidy.  Shocks are therefore element-specific."]
    if with_retaliation:
        note += ["",
                 f"NETTED with the {RETALIATION['ZAF']:.0f}pp retaliatory tariff on USA",
                 "goods (Table 7), phased half in 2026 and half in 2027.  For the",
                 "USA source these two policies act on the same component and are",
                 "combined into a single shock below."]
    L = hdr(f"South African import tariffs -- step {k} of {n}", note)
    zi = REG.index("ZAF")

    def rate(step):
        """Applied rate in year `step` (0 = initial), per cent, by component."""
        out = {}
        for i in range(16):
            for r in REG:
                if r == "ZAF":
                    continue
                t0 = rt[i, REG.index(r), zi]
                t = t0 * (1.0 - TARIFF_CUT_TOTAL * step / n)
                if with_retaliation and r == "USA":
                    phase = min(step, 2) / 2.0          # half 2026, half 2027
                    t += RETALIATION["ZAF"] * phase
                out[(i, r)] = t
        return out

    prev, curr = rate(k - 1), rate(k)
    for i in range(16):
        for r in REG:
            if r == "ZAF":
                continue
            p, c = prev[(i, r)], curr[(i, r)]
            if p == 0.0 and c == 0.0:
                continue
            tag = "  [cut + retaliation]" if (with_retaliation and r == "USA") else ""
            L.append(f'shock tms("{SEC[i]}","{r}","ZAF") = {power_shock(p, c):8.4f} ; '
                     f'! {p:7.3f}% -> {c:7.3f}%{tag}')
    L.append("")
    return L


def depreciation(k, per_year):
    n = len(DEP_YEARS)
    return hdr(f"Real exchange rate adjustment -- step {k} of {n}",
               [f"Trade-balance-to-income RATIO raised by {per_year:+.5f} per year",
                f"over {DEP_YEARS[0]}-{DEP_YEARS[-1]}, i.e. {per_year*n:+.5f} cumulatively",
                f"({per_year*n*100:+.3f} percentage points of regional income).",
                f"Calibrated to deliver a {per_year*n/0.01484:.2f}% cumulative real",
                "depreciation -- the minimum sufficient to offset the aggregate",
                "impact of the USA tariff shock.",
                "Requires Swap dpsave(\"ZAF\") = DTBALR(\"ZAF\") in the closure.",
                "The real depreciation is the model's ENDOGENOUS response to this,",
                "not an imposed price.  Read it off pfactor(ZAF) minus pfactwld.",
                "",
                "MUST be 'ashock': DTBALR is exogenous under POL2/POL3, so RunDynam",
                "also writes a base-case shock for it.  'shock' would specify the",
                "same component twice and GEMPACK would stop.",
                "",
                "CALIBRATE this value - see README section 6."]) + \
        [f'ashock DTBALR("ZAF") = {per_year:9.5f} ;', ""]


def dsm_block(targets):
    L = hdr("DSM realistic export opportunity targets (Q2 + Q3)",
            ["qxs is exogenous under POL3 and ams is the endogenous residual.",
             "ams is therefore a CALIBRATED OUTCOME reporting the effective",
             "market-access improvement required to deliver these volumes.",
             "Values are the authors' DSM output after the realisation",
             "discounts of Section 4.7.6.  ZAF->USA is excluded by assumption.",
             "MUST be 'tshock': qxs is exogenous under POL3, so RunDynam also",
             "writes a base-case shock for it.  'tshock' supplies the TOTAL",
             "value and replaces the base-case statement; 'shock' would clash."])
    for s_, d, v in targets:
        L.append(f'tshock qxs("{s_}","ZAF","{d}") = {v:8.4f} ;')
    L.append("")
    return L


def write(out, name, lines):
    p = os.path.join(out, name)
    with open(p, "w", newline="\r\n") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    print(f"  {name:20s} {len(lines):5d} lines")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--har", default="data/BaseRate.har")
    ap.add_argument("--out", default="Shocks")
    ap.add_argument("--rates", default="data/base_rates_RTMS.csv")
    ap.add_argument("--dsm", default="data/dsm_qxs_targets.csv")
    ap.add_argument("--no-fx", action="store_true",
                    help="omit the DTBALR shock entirely; the real depreciation "
                         "is then a pure endogenous outcome of the tariff cut "
                         "and the labour-market closure (use with POL1/POL2N)")
    ap.add_argument("--dtbalr", type=float, default=DTBALR_PER_YEAR,
                    help="DTBALR shock, percentage points of income per year")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rt = load_rtms(a.har, a.rates)
    dsm = load_dsm(a.dsm)
    print(f"Writing to {a.out}/")

    zaf = us_tariff_on_zaf(rt)
    third = us_tariff_on_third(rt)

    # Scenario 1 -------------------------------------------------------------
    write(a.out, "TTSS25.PSH", ["! Scenario 1: USA tariff shock. Period 2025.", ""] + zaf)

    # Scenario 3 -------------------------------------------------------------
    write(a.out, "TTSSW25.PSH",
          ["! Scenario 3: USA tariff shock + world response. Period 2025.", ""]
          + zaf + third)
    for j, y in enumerate([2026, 2027], start=1):
        write(a.out, f"TTSSW{str(y)[2:]}.PSH",
              [f"! Scenario 3: retaliation phase {j}. Period {y}.", ""]
              + retaliation(rt, j))

    # Scenario 2 -------------------------------------------------------------
    write(a.out, "SAPR25.PSH", ["! Scenario 2: SA policy response. Period 2025.", ""] + zaf)
    for k, y in enumerate(CUT_YEARS, start=1):
        write(a.out, f"SAPR{str(y)[2:]}.PSH",
              [f"! Scenario 2: SA policy response. Period {y}.", ""]
              + ([] if a.no_fx else depreciation(k, a.dtbalr))
              + sa_import_tariffs(rt, k, False))

    # Scenario 4 -------------------------------------------------------------
    write(a.out, "SAPRW25.PSH",
          ["! Scenario 4: SA policy response + world response. Period 2025.", ""]
          + zaf + third)
    for k, y in enumerate(CUT_YEARS, start=1):
        body = ([] if a.no_fx else depreciation(k, a.dtbalr)) \
            + sa_import_tariffs(rt, k, True)
        if y in (2026, 2027):
            body += retaliation(rt, 1 if y == 2026 else 2, exclude_zaf=True)
        write(a.out, f"SAPRW{str(y)[2:]}.PSH",
              [f"! Scenario 4: SA policy + world response. Period {y}.", ""] + body)

    # Scenario 5 -------------------------------------------------------------
    # Carries the full Scenario 4 shock set for the year PLUS the DSM targets,
    # so Scenario 5 nests Scenario 4 exactly.  2025 uses SAPRW25.PSH.
    for k, y in enumerate(CUT_YEARS, start=1):
        body = ([] if a.no_fx else depreciation(k, a.dtbalr)) \
            + sa_import_tariffs(rt, k, True)
        if y in (2026, 2027):
            body += retaliation(rt, 1 if y == 2026 else 2, exclude_zaf=True)
        body += dsm_block(dsm[y])
        write(a.out, f"SADSM{str(y)[2:]}.PSH",
              [f"! Scenario 5: SA policy + world response + DSM realisation. Period {y}.",
               "! Nests the complete Scenario 4 shock set for this year.", ""] + body)

    # self-check ------------------------------------------------------------
    print("\nSelf-check")
    zi = REG.index("ZAF")
    lev = {(SEC[i], r): rt[i, REG.index(r), zi]
           for i in range(16) for r in REG
           if r != "ZAF" and rt[i, REG.index(r), zi] > 0}
    init = dict(lev)
    neg = 0
    for y in CUT_YEARS:
        txt = open(os.path.join(a.out, f"SAPR{str(y)[2:]}.PSH"), encoding="latin-1").read()
        for m in re.finditer(r'shock tms\("([^"]+)","([^"]+)","ZAF"\) =\s*(-?[\d.]+)', txt):
            key = (m.group(1), m.group(2))
            new = (1 + lev[key] / 100) * (1 + float(m.group(3)) / 100) - 1
            lev[key] = new * 100
            if new < 0:
                neg += 1
    err = max(abs(lev[k] - 0.5 * init[k]) for k in lev)
    import collections
    dups = 0
    for fn in sorted(os.listdir(a.out)):
        txt = open(os.path.join(a.out, fn), encoding="latin-1").read()
        comps = re.findall(r'^\s*(?:a|t)?shock\s+(\w+\([^)]*\))', txt, re.M)
        d = [c for c, n_ in collections.Counter(comps).items() if n_ > 1]
        if d:
            dups += len(d)
            print(f"  !! {fn}: {len(d)} component(s) shocked twice, e.g. {d[0]}")
    print(f"  components shocked twice in any file ...... {dups}   (must be 0)")
    print(f"  negative post-shock tariff rates .......... {neg}   (must be 0)")
    print(f"  max |final rate - 50% of base| ............ {err:.2e}   (must be ~0)")
    tot=a.dtbalr*len(DEP_YEARS)
    print(f"  DTBALR shock .............................. "
          f"{a.dtbalr:.5f}/yr, {tot:.5f} cumulative "
          f"({tot*100:.3f} pp of income)")
    print(f"  implied real depreciation ................. {tot/0.01484:.3f}% "
          f"(sensitivity 0.01484 per 1%, from Test D)")
    if neg or dups or err > 1e-3:
        raise SystemExit("SELF-CHECK FAILED - do not run these files.")
    print("  OK")


if __name__ == "__main__":
    main()
