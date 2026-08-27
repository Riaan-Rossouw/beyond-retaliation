# Tariff shock verification

`verify_tariffs.py` reconstructs every realised bilateral tariff rate from the
model solution and compares it against the intended rate.

```
realised = (1 + t_base/100) * (1 + tms_devc/100) - 1
```

The power form matters: `tms` is the percentage change in the **power** of the
tariff, (1+t), not in the ad valorem rate. A shock of `-50` halves the power, so
a 10% tariff becomes **−45%** — a 45% import subsidy, not a 5% tariff.

## Running it

```bash
python verify_tariffs.py --results /path/to/run/folders --rates ../data/base_rates_RTMS.csv
```

`--results` should contain `S1_TTSS/`, `S2_SAPR/`, `S3_TTSSW/`, `S4_SAPRW/`,
`S6_TTSRET/`, each with `BAUB-BRRR-POLP-devc.csv`. Missing folders are skipped.
Exit status is non-zero if any cell is outside the 0.02 percentage point tolerance.

## What it checks

| Check | Intended rate |
|---|---|
| Sc 1 USA tariff on ZAF goods | base + 30 × (1 − exempt share) |
| Sc 1 no unintended movement | only ZAF→USA cells may move |
| Sc 2 unilateral cut | 50% of base |
| Sc 3 USA tariffs on third countries | base + 30/15/10pp, Coal and Mining exempt |
| Sc 3 retaliation | base + 32/20/20/10/10/10pp by region |
| Sc 4 netted case | ½ base + 10pp on the USA source |
| Sc 6 retaliation only | base + 10pp |

Scenario 4 is the one worth watching: the unilateral cut and the retaliatory
tariff both act on `tms(i,"USA","ZAF")`. Emitting them as two statements makes
GEMPACK stop with *"Some components of tms have been specified more than once"*;
they must be netted into a single path.

`verification_output.txt` holds the result for the runs reported in the paper.
