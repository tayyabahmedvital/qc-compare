"""Tests for compare_qc. The regression tests rebuild Kakit's sheets from his inputs and diff them."""

import csv
from pathlib import Path

import pandas as pd
import pytest

import compare_qc as qc

HERE = Path(__file__).parent
PREFIX = "QC compare tool 2026-10-06 - "
FLAGGER = HERE / "outputs" / f"{PREFIX}rf output - absqc.csv"


def sheet_rows(path):
    """A sheet export as rows, without the empty padding rows spreadsheets append."""
    with open(path, newline="") as f:
        return [row for row in csv.reader(f) if row[0]]


@pytest.mark.parametrize("truth, sheet, runs_label, flagger_without", [
    # Kakit's uf-only sheet shows HBA1C1 as all Not Found although the saved flagger tab has values
    # for it (his absqc+AD sheet uses them), so that column is left out of the flagger here.
    ("truth (uf only)", "absqc-uf only", "Total runs with data", ["HBA1C1"]),
    ("truth (uF+AD)", "absqc+AD", "Total runs with QC truth data", []),
])
def test_rebuilds_kakits_sheet(tmp_path, truth, sheet, runs_label, flagger_without):
    labels = qc.compare(qc.load_truth(HERE / "inputs" / f"{PREFIX}{truth}.csv"),
                        qc.load_flagger(FLAGGER).drop(columns=flagger_without), pad=4)
    qc.write_all(labels, "check", tmp_path, runs_label)
    expected = sheet_rows(HERE / "outputs" / f"{PREFIX}fail comparison - {sheet}.csv")
    assert sheet_rows(tmp_path / "fail comparison - check.csv") == expected


def test_all_truth_layouts_load_the_same_assays():
    names = {tuple(qc.load_truth(p).columns) for p in (HERE / "inputs").glob("*.csv")}
    assert names == {tuple(qc.STRUCTURE)}


def test_filtered_page_keeps_only_rows_with_caught_or_miss(tmp_path):
    truth = pd.DataFrame({"HDL": ["FAIL", "FAIL", "PASS", "PASS"], "ALP": ["PASS"] * 4},
                         index=["caught", "miss", "good", "wrong"])
    flagger = pd.DataFrame({"HDL": ["FAIL", "PASS", "PASS", "FAIL"], "ALP": ["PASS"] * 4},
                           index=["caught", "miss", "good", "wrong"])
    labels = qc.compare(truth, flagger)
    assert labels.iloc[:, 0].tolist() == ["CAUGHT", "MISS", "GOOD", "WRONG"]

    qc.write_all(labels, "t", tmp_path)
    filtered = sheet_rows(tmp_path / "fail comparison - t (CAUGHT-MISS only).csv")
    assert [row[0] for row in filtered[qc.FIRST_RUN_ROW - 1:]] == ["caught", "miss"]
    assert filtered[0][1:] == ["4", "4"]  # stats still describe all runs


def test_not_found_and_blank_truth_cases():
    truth = pd.DataFrame({"HDL": ["FAIL", ""], "ALP": ["FAIL", ""]}, index=["a", "b"])
    flagger = pd.DataFrame({"HDL": ["FAIL", "FAIL", "PASS"]}, index=["a", "b", "c"])  # no ALP column, no truth row for c
    labels = qc.compare(truth, flagger)
    assert labels.to_numpy().tolist() == [["CAUGHT", "Not Found"], ["WRONG", "Not Found"],
                                          ["Not Found", "Not Found"]]


def test_stats_use_div0_when_a_denominator_is_empty():
    labels = qc.compare(pd.DataFrame({"HDL": ["PASS"]}, index=["a"]),
                        pd.DataFrame({"HDL": ["PASS"]}, index=["a"]))
    rows = qc.stats(labels, "runs")
    assert [row[1] for row in rows] == [1, 0, 0, 0, 0.0, qc.DIV0, 1.0]


def test_flagger_rejects_values_other_than_pass_fail(tmp_path):
    bad = tmp_path / "flagger.csv"
    bad.write_text("run_code,HDL\na,TRUE\n")
    with pytest.raises(ValueError, match="PASS/FAIL"):
        qc.load_flagger(bad)
