# Beyond Retaliation: replication package

Closure files, shock files and summary results for the simulations reported in

> Rossouw, R., Cameron, M.J. and Naudé, W. (2026). *Beyond Retaliation: How South
> Africa Can Effectively Counter the USA's Tariff Wars.*

**Model:** GDyn v3.6 (GTAP-Dynamic), solved with GEMPACK / RunDynam.
**Database:** GTAP 11, 2017 reference year, aggregated to **16 sectors × 7 regions
× 5 factors** using `Aggregation/gtp15_7.agg`.

Neither the GDyn model source nor the GTAP 11 database is redistributed here,
both are licensed separately. See [Obtaining the model and data](#obtaining-the-model-and-data).

---

## Scenarios

| # | Name | Question it answers |
|---|---|---|
| 1 | USA reciprocal tariff on South African goods | What does the tariff shock cost? |
| 2 | Sc 1 + unilateral 50% tariff cut + calibrated real depreciation | Does liberalisation help? |
| 3 | Sc 1 + USA tariffs on third countries + global retaliation | What does a global trade war do? |
| 4 | Sc 2 + Sc 3 | Does the policy response work inside a trade war? |
| 5 | Sc 4 + realisation of DSM export potential | What is export diversification worth? |
| 6 | Sc 1 + South African retaliation only | **Is retaliation optimal?** |

Scenario 6 is the clean test of the retaliation question. Scenario 3 cannot answer
it, because it bundles South Africa's retaliation with USA tariffs on China, the
EU and others.

## Run sequence

Each scenario runs 2018→2030 in annual steps. Periods 2018–2024 are baseline only.

| Sc | 2025 | 2026 | 2027 | 2028–2030 |
|---|---|---|---|---|
| 1 | POL1 + `TTSS25` | POL1 | POL1 | POL1 |
| 2 | POL2 + `SAPR25` | POL2 + `SAPR26` | POL2 + `SAPR27` | POL2 + `SAPR28–30` |
| 3 | POL1 + `TTSSW25` | POL1 + `TTSSW26` | POL1 + `TTSSW27` | POL1 |
| 4 | POL2 + `SAPRW25` | POL2 + `SAPRW26` | POL2 + `SAPRW27` | POL2 + `SAPRW28–30` |
| 5 | POL2 + `SAPRW25` | POL3F + `SADSM26` | POL3F + `SADSM27` | POL3F + `SADSM28–30` |
| 6 | POL1 + `TTSS25` | POL1 + `TTSRET26` | POL1 + `TTSRET27` | POL1 |

Base case: `BASB.CLS` with `Y17-18.BSH` … `Y29-30.BSH`.
Rerun: `BASR.CLS`, 2025–2030, no policy shocks. `POLS.CLS` is the standard E0-DYN closure.

**Solver:** Gragg, steps 4 8 12 (6 12 18 for Scenario 5), 6 subintervals,
automatic accuracy on, 4 accuracy figures, 99%, criterion Solution.

## Closures

| File | Swaps | Used by |
|---|---|---|
| `POL1.CLS` | fixed unskilled wage; fiscal neutrality | Sc 1, 3, 6 |
| `POL2.CLS` | POL1 + `dpsave ↔ DTBALR` | Sc 2, 4; Sc 5 in 2025 |
| `POL3F.CLS` | POL2 + 46 `ams ↔ qxs` swaps | Sc 5, 2026–2030 |

**Fiscal neutrality (`tp ↔ del_ttaxr`) is required** alongside the fixed-wage
closure. Without revenue replacement the unemployment closure produces an
illusory employment gain as the real wage falls automatically.

**The real exchange rate uses `dpsave ↔ DTBALR`**, the standard current-account
closure: the trade balance is exogenous and the depreciation is the model's
endogenous response.

## Three things that are easy to get wrong

**1. `tms` is the power of the tariff, not the rate.** A shock of `-50` takes
(1+t) to 0.5(1+t), so a 10% tariff becomes **−45%** — a 45% import subsidy.
Halving the *rate* requires element-specific shocks,
`100·[(1+t_new)/(1+t_old) − 1]`, which `build_shocks.py` generates from `RTMS`.

**2. `DTBALR` is a fraction, not percentage points.** From `gdyn_v36s.tab`:

```
100 * INCOME(r) * DTBALR(r) = 100 * DTBAL(r) - TBAL(r) * y(r)
```

so `DTBALR = [DTBAL − TBAL·y/100] / INCOME`. A value of 0.50 means a **fifty
percentage point of income** swing in the trade balance. The shock used here is
`0.00030` per year.

**3. RunDynam shock keywords are not interchangeable.** RunDynam writes a
base-case shock for every variable exogenous in the policy closure, including
ones made exogenous by a `Swap`. Plain `shock` on the same component makes
GEMPACK stop with *"Some components of X have been specified more than once"*.

| Keyword | Meaning | Used for |
|---|---|---|
| `shock` | absolute, straight to GEMPACK | `tms` |
| `ashock` | **added** to the base-case shock | `DTBALR` |
| `tshock` | **total**, replaces the base-case shock | `qxs` |

## Calibration of the depreciation

The depreciation is not imposed. It is calibrated from a single-year probe:
`DTBALR = 0.00916` produced a 0.6173% real depreciation, giving **0.01484 per 1%**.

Scenario 1 costs 0.478% of real exports, 0.200% of real GDP and US$803m of
welfare; restoring each requires 0.069%, 0.044% and 0.051% respectively. The
shock is set to `0.00030` per year over 2026–2030, and the five-year cumulative
response delivers **0.60%**, comfortably above the offset requirement and an
order of magnitude below the 15% assumed in earlier drafts.

A 15% depreciation is not attainable: it would require the trade balance to move
from 7.3% to 76% of income, with imports falling 103%.

## Rebuilding the shock files

The `Shocks/` folder is already built. The generator is included so every number
can be traced to its source.

**Windows:** double-click `Build_Shocks.bat`, or

```bat
cd /d "C:\path\to\beyond-retaliation"
Build_Shocks.bat
```

**macOS / Linux:**

```bash
python3 -m pip install numpy
python3 build_shocks.py
```

By default it reads `data/base_rates_RTMS.csv`, so no GEMPACK toolchain is needed.
To read the rates from your own aggregated database, put `BaseRate.har` in `data/`
and pass `--har data/BaseRate.har` (requires
[HARPY](https://github.com/GEMPACKsoftware/HARPY)).

The self-check refuses to write if any component is shocked twice, if any
post-shock tariff rate is negative, or if the tariff cut does not land at exactly
50% of base:

```
components shocked twice in any file ...... 0
negative post-shock tariff rates .......... 0
max |final rate - 50% of base| ............ 1.85e-04
DTBALR shock .............................. 0.00030/yr, 0.00150 cumulative
implied real depreciation ................. 0.101%
OK
```

## Verifying a run

In `BAUB-BRRR-POLP-devc.csv` at 2030:

| Variable | Expected |
|---|---|
| `incomeslack(ZAF)` | 0 — the regional accounts close |
| `del_ttaxr(ZAF)` | 0 — fiscal neutrality binds |
| `dpsave(ZAF)` | non-zero in Sc 2, 4, 5 |
| `DTBALR(ZAF)` | ≈ 0.00150 in Sc 2, 4, 5 |
| `tms(i,USA,r)` | rises in Sc 3, 4, 5, 6 only |

## Obtaining the model and data

- **GDyn model** — free from the [GTAP website](https://www.gtap.agecon.purdue.edu/models/Dynamic/). Requires [GEMPACK](https://www.copsmodels.com/gempack.htm).
- **GTAP 11 Data Base** — licensed; purchase from [GTAP](https://www.gtap.agecon.purdue.edu/databases/v11/).
- **Aggregation** — run GTAPAgg2 with `Aggregation/gtp15_7.agg` against the GTAP 11
  2017 GDyn source to produce `basedata.har`, `BaseRate.har`, `sets.har`,
  `default.prm`, `gdpextra.har`, `GTAPSAM.har`, `BaseView.har`.

## Contents

```
Closures/     BASB, BASR, POLS, POL1, POL2, POL3F (.CLS); Y17-18…Y34-35 (.BSH)
Shocks/       TTSS25, TTSSW25–27, TTSRET26–27, SAPR25–30, SAPRW25–30, SADSM26–30
Aggregation/  gtp15_7.agg
data/         base_rates_RTMS.csv, dsm_qxs_targets.csv
Results/      BeyondRetaliation_Summary_Results.xlsx  (Tables 9–12 and charts)
build_shocks.py, Build_Shocks.bat, README.md, LICENSE
```

## Licence

CC BY 4.0 — see `LICENSE`. Covers the files in this repository only, not the
GTAP database or the GDyn/GEMPACK software.

## Citation

> Rossouw, R., Cameron, M.J. and Naudé, W. (2026). *Beyond Retaliation: How South
> Africa Can Effectively Counter the USA's Tariff Wars.* Replication package.
> Zenodo. [DOI on release]
