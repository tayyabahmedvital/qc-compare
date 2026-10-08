# qc-compare

Automates Kakit's "fail comparison" sheet: compares a results-flagger table with the
ground-truth PASS/FAIL table and labels every (run, assay) cell.

```
pip install -r requirements.txt
python compare_qc.py --truth "inputs/<truth>.csv" --flagger "<flagger>.csv" --check absqc-uf-only
python -m pytest
```

- **Truth**: any of the three exports in `inputs/` (header layout is detected).
- **Flagger**: `run_code` plus one PASS/FAIL column per assay (the "rf output" tab).
- **Output** (`--out`, default `outputs/`): `fail comparison - <check>.csv` (all runs),
  `... (CAUGHT-MISS only).csv` (rows with a CAUGHT or MISS) and a coloured `.xlsx` with both pages.
- Labels: CAUGHT, MISS, GOOD, WRONG (false positive), Not Found. See the docstring in `compare_qc.py`.
- `--runs-label` sets the first stats row's text ("Total runs with QC truth data" in the AD sheet);
  `--pad 0` drops the 4 blank trailing columns Kakit's sheets carry.
