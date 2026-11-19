"""Summarize author-reported historical PCA10040 measurements.

These numbers are provided by the project author; the raw instrument traces
have not been included. This tool performs arithmetic, not data acquisition.
"""
import csv
from pathlib import Path

REFERENCE_CSV = Path(__file__).with_name("reference_values.csv")
EXPECTED = {"Bare-metal standard", "Bare-metal optimized", "Zephyr RTOS System OFF"}


def load_references(path=REFERENCE_CSV):
    with open(path, newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 3 or {row["variant"] for row in rows} != EXPECTED:
        raise ValueError("Expected exactly the three named reference variants")
    for row in rows:
        if row["origin"] != "author-reported measurement on PCA10040":
            raise ValueError("Measurement origin must be documented")
        if row["verification"] != "raw traces not supplied in repository":
            raise ValueError("Missing-trace status must be explicit")
        if float(row["current_uA"]) <= 0:
            raise ValueError("Current must be positive")
    return {row["variant"]: float(row["current_uA"]) for row in rows}


def percent_difference(test, baseline):
    if baseline <= 0:
        raise ValueError("Baseline must be positive")
    return (test / baseline - 1.0) * 100.0


def main():
    values = load_references()
    zephyr = values["Zephyr RTOS System OFF"]
    print("AUTHOR-REPORTED PCA10040 MEASUREMENTS (RAW TRACES NOT INCLUDED)")
    for name, current in values.items():
        print(f"{name}: {current:.1f} µA")
    for baseline in ("Bare-metal standard", "Bare-metal optimized"):
        diff = percent_difference(zephyr, values[baseline])
        print(f"Zephyr vs {baseline}: {diff:+.1f}%")


if __name__ == "__main__":
    main()
