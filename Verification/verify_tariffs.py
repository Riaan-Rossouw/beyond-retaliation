#!/usr/bin/env python3
"""
verify_tariffs.py -- check that the tariff shocks LANDED as intended.

Reconstructs each realised bilateral tariff rate from the model solution:

    realised = (1 + t_base/100) * (1 + tms_devc/100) - 1

because tms is the percentage change in the POWER of the tariff (1+t), not in
the ad valorem rate. Compares against the intended rate for every scenario.

Usage:
    python verify_tariffs.py --results /path/to/S1_TTSS/.. --rates ../data/base_rates_RTMS.csv
"""
import argparse, csv, os, sys

SEC = ["GrainCrop", "LiveMeat", "OthAgFood", "Coal", "Mining", "Metals", "Auto",
       "MachEquip", "ChemPlast", "TexApp", "OthManuf", "Utilities", "Construct",
       "TradeTran", "BusSvc", "PubOthSvc"]
MERCH = SEC[:11]
REG = ["ZAF", "USA", "SACUSADC", "CHN", "EU27", "GBR", "ROW"]

EXEMPT = {"GrainCrop": 0.00, "LiveMeat": 0.00, "OthAgFood": 0.02, "Coal": 1.00,
          "Mining": 0.87, "Metals": 0.50, "Auto": 0.00, "MachEquip": 0.08,
          "ChemPlast": 0.20, "TexApp": 0.00, "OthManuf": 0.05}
STATUTORY = 30.0
US_ON_THIRD = {"CHN": 30.0, "EU27": 15.0, "GBR": 10.0, "SACUSADC": 15.0, "ROW": 15.0}
US_THIRD_EXEMPT = {"Coal", "Mining"}
RETALIATION = {"CHN": 32.0, "EU27": 20.0, "GBR": 20.0, "ZAF": 10.0,
               "SACUSADC": 10.0, "ROW": 10.0}
CUT = 0.50
TOL = 0.02


def load_rates(path):
    r = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            r[(row["sector"], row["source"], row["destination"])] = float(row["rate_pct"])
    return r


def load_devc(path):
    d = {}
    with open(path, newline="", encoding="latin-1") as f:
        for row in csv.reader(f):
            if not row or not row[0] or row[0] in ("Control", "Solution", "Deviation"):
                continue
            v = []
            for c in row[1:]:
                c = c.strip()
                if not c:
                    continue
                try:
                    v.append(float(c))
                except ValueError:
                    pass
            if v:
                d[row[0].strip()] = v
    return d


def realised(t0, tms):
    return ((1 + t0 / 100.0) * (1 + tms / 100.0) - 1) * 100.0


def check(name, cases, dev, rates, fails):
    n = bad = 0
    worst = ("", 0.0)
    for sec, src, dst, target in cases:
        key = f"tms({sec}:{src}:{dst})"
        if key not in dev:
            continue
        t0 = rates.get((sec, src, dst), 0.0)
        got = realised(t0, dev[key][-1])
        err = abs(got - target)
        n += 1
        if err > TOL:
            bad += 1
            fails.append(f"{key}: intended {target:.3f}%, realised {got:.3f}%")
        if err > worst[1]:
            worst = (key, err)
    flag = "OK  " if bad == 0 else "FAIL"
    print(f"  [{flag}] {name:52s} {n:4d} cells, {bad} bad, worst {worst[1]:.4f}pp")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=".", help="folder holding S1_TTSS/ .. S6_TTSRET/")
    ap.add_argument("--rates", default="../data/base_rates_RTMS.csv")
    a = ap.parse_args()
    rates = load_rates(a.rates)
    fails, total = [], 0

    def dev(folder):
        p = os.path.join(a.results, folder, "BAUB-BRRR-POLP-devc.csv")
        if not os.path.exists(p):
            print(f"  [SKIP] {folder}: {p} not found")
            return None
        return load_devc(p)

    print("Tariff shock verification\n")

    d = dev("S1_TTSS")
    if d:
        cases = [(s, "ZAF", "USA",
                  rates.get((s, "ZAF", "USA"), 0.0) + STATUTORY * (1 - EXEMPT[s]))
                 for s in MERCH]
        total += check("Sc 1  USA tariff on ZAF goods", cases, d, rates, fails)
        moved = [k for k, v in d.items() if k.startswith("tms(") and abs(v[-1]) > 1e-6]
        stray = [k for k in moved if not k.endswith(":ZAF:USA)")]
        print(f"  [{'OK  ' if not stray else 'FAIL'}] "
              f"{'Sc 1  no unintended tariff movement':52s} {len(stray)} stray cells")
        total += len(stray)

    d = dev("S2_SAPR")
    if d:
        cases = [(s, r, "ZAF", CUT * rates[(s, r, "ZAF")])
                 for s in SEC for r in REG
                 if r != "ZAF" and rates.get((s, r, "ZAF"), 0.0) > 0]
        total += check("Sc 2  SA unilateral 50% tariff cut", cases, d, rates, fails)

    d = dev("S3_TTSSW")
    if d:
        cases = [(s, r, "USA",
                  rates.get((s, r, "USA"), 0.0) + (0 if s in US_THIRD_EXEMPT else pp))
                 for r, pp in US_ON_THIRD.items() for s in MERCH]
        total += check("Sc 3  USA tariffs on third countries", cases, d, rates, fails)
        cases = [(s, "USA", r, rates.get((s, "USA", r), 0.0) + pp)
                 for r, pp in RETALIATION.items() for s in MERCH]
        total += check("Sc 3  retaliation on USA goods", cases, d, rates, fails)

    d = dev("S4_SAPRW")
    if d:
        cases = [(s, "USA", "ZAF",
                  CUT * rates.get((s, "USA", "ZAF"), 0.0) + RETALIATION["ZAF"])
                 for s in MERCH]
        total += check("Sc 4  netted cut + retaliation (USA source)", cases, d, rates, fails)

    d = dev("S6_TTSRET")
    if d:
        cases = [(s, "USA", "ZAF",
                  rates.get((s, "USA", "ZAF"), 0.0) + RETALIATION["ZAF"]) for s in MERCH]
        total += check("Sc 6  SA retaliation only", cases, d, rates, fails)

    print()
    if fails:
        print(f"{len(fails)} failures:")
        for f in fails[:20]:
            print("   ", f)
        sys.exit(1)
    print(f"All checks passed within {TOL} percentage points.")


if __name__ == "__main__":
    main()
