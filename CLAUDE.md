# qc-compare

Script that automates Kakit's manual Google Sheets process: compare a **results-flagger output**
against the **ground-truth PASS/FAIL table** and produce the "fail comparison" sheet.
Part of the QC Hunt ("Tools required: compare QC tables"). Sibling repo: `~/QCTrainer`
(`qc_thresholds` finds the thresholds; the flagger applies them; this tool scores the flagger).

## How to work in this repo
- Owner is a data/software intern; explain reasoning before code, one piece at a time, ask before
  architecture decisions.
- Keep code to the `skills/SKILL (2).md` thermo-nuclear standard: direct, boring, no wrappers,
  no scattered special cases.
- Do not commit data; do not overwrite Kakit's sample sheets in `outputs/`.

## What the tool does
`compare_qc.py` (one module) reads a truth CSV and a flagger CSV and labels each (run, assay) cell:

| truth | flagger | label |
|---|---|---|
| FAIL | FAIL | CAUGHT |
| FAIL | PASS | MISS |
| not FAIL (PASS/blank) | PASS | GOOD |
| not FAIL | FAIL | WRONG (false positive) |
| any | no value, or run not in truth | Not Found |

Stats block (rows 1-7): total runs, failure count (CAUGHT+MISS), detected (CAUGHT), false positives
(WRONG), prevalence, sensitivity = CAUGHT/(CAUGHT+MISS), specificity = GOOD/(GOOD+WRONG);
`#DIV/0!` when the denominator is 0. Rows follow the flagger's run order.

**Inputs**
- `--truth`: any export in `inputs/` (`truth (uf only)`, `truth (uF+AD)`, `well_response-FS01`);
  the assay-name header row is auto-detected.
- `--flagger`: `run_code` + one PASS/FAIL column per assay (the "rf output" tab).
- `--check` (name for output files), `--out`, `--runs-label`, `--pad` (default 4 blank trailing columns).

**Outputs** (three files per check): full CSV, `(CAUGHT-MISS only)` CSV, and one coloured `.xlsx`
with both pages.

Run from the repo root:
```
python compare_qc.py --truth "inputs/QC compare tool 2026-10-06 - truth (uf only).csv" --flagger "outputs/QC compare tool 2026-10-06 - rf output - absqc.csv" --check "absqc-uf only" --out results
python -m pytest
```

## Files
- `compare_qc.py` - the tool. `STRUCTURE` (assay -> structure, the 20 uF assays) is the one hard-coded map.
- `test_compare_qc.py` - regression tests rebuild Kakit's sheets from `inputs/` + the flagger file; unit tests for labels, stats, filter, loaders.
- `inputs/` - truth tables. `outputs/` - Kakit's sample sheets (expected results) plus the flagger file `rf output - absqc.csv` (an input, misplaced here).
- `skills/` - the code-quality review skill.

## Data notes
- `truth (uF+AD)` is identical to `well_response-FS01` (350 runs). `truth (uf only)` has 351 runs
  (extra `2026AUG28-FS01_1B_INS26_RUN34-3`) and 58 cells differ: it is the uF-only variant.
- Use `truth (uf only)` to reproduce the uf-only sheet, `truth (uF+AD)`/`well_response` for absqc+AD.
- Never truthiness-test PASS/FAIL strings; the tool compares against the literal strings.

## Chat history
1. Explored `~/QCTrainer` (the QC Hunt: threshold finder, run_index, sweeps, Results Flagger) to understand context; no changes.
2. Reverse-engineered the label and stats rules from Kakit's sample sheets (verified on all 3 sheets), planned, then built the tool + tests.
3. Explained the files and inputs; compared the truth files; moved everything out of the initial `fail_comparison/` folder to the repo root; wrote this file.

## Progress
- Done: `compare_qc.py`, 7 passing tests. absqc+AD sheet reproduced exactly; absqc-uf only reproduced except HBA1C1.
- Not yet: user has not run the tool; `.xlsx` not inspected in Excel/Sheets; nothing committed.
- Empty `fail_comparison/` folder may remain (was locked); delete by hand.

## Known issues / open questions
- Kakit's uf-only sheet shows HBA1C1 as all Not Found, but the saved flagger tab has values for it
  (his absqc+AD sheet uses them). Probably an older flagger tab; ask Kakit. The test drops HBA1C1 for this case.
- Imgstat sample cannot be verified: no imgstat flagger file yet.
- Which truth file does Kakit's current process use? Which flagger maps to which sheet?
- Only the wide flagger format (run_code + assay columns) is supported.

## Next steps
1. Run both commands on the real files and check the results (CSV and xlsx) against Kakit's sheets.
2. Get the imgstat / AD flagger files from Kakit and verify those checks.
3. Move `rf output - absqc.csv` into `inputs/` (update the test path).
4. If other assay sets are needed (HT, IA), make `STRUCTURE` configurable (e.g. read from a CSV).
5. Decide whether to drop the 4 padding columns by default; commit once reviewed.
