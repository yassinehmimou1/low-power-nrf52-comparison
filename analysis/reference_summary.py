"""Summarize user-provided, unverified community reference currents.

This script is NOT a measurement tool and does not create hardware evidence.
"""
import csv
from pathlib import Path

REFERENCE_CSV = Path(__file__).with_name("reference_values.csv")


def load_references(path=REFERENCE_CSV):
    with open(path, newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    expected = {
        "Bare-metal standard", "Bare-metal optimized", "Zephyr RTOS System OFF"
    }
    if {row["variant"] for row in rows} != expected or len(rows) != 3:
        raise ValueError("Expected exactly the three named reference variants")
    if any(row["verification"] != "unverified" for row in rows):
        raise ValueError("Reference data must be clearly marked unverified")
    return {row["variant"]: float(row["current_uA"]) for row in rows}


def percent_difference(test, baseline):
    if baseline <= 0:
        raise ValueError("Baseline must be positive")
    return (test / baseline - 1.0) * 100.0


def main():
    values = load_references()
    zephyr = values["Zephyr RTOS System OFF"]
    print("COMMUNITY-REPORTED REFERENCES — NOT VERIFIED ON THIS FIRMWARE")
    for name, current in values.items():
        print(f"{name}: {current:.1f} µA")
    for baseline in ("Bare-metal standard", "Bare-metal optimized"):
        diff = percent_difference(zephyr, values[baseline])
        print(f"Zephyr vs {baseline}: {diff:+.1f}%")


if __name__ == "__main__":
    main()
