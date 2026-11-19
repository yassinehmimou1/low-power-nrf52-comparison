#!/usr/bin/env python3
"""Analyze sampled current/voltage traces from the nRF52 comparison.

CSV columns required:
    timestamp_s,implementation,current_mA,voltage_V,data_origin
Optional:
    phase,run_id
`data_origin` must be MEASURED or SIMULATED. Results are grouped by
(implementation, data_origin, run_id), so runs and synthetic/physical data are not mixed.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REQUIRED_COLUMNS = {
    "timestamp_s", "implementation", "current_mA", "voltage_V", "data_origin"
}
VALID_ORIGINS = {"MEASURED", "SIMULATED"}


@dataclass(frozen=True)
class Sample:
    timestamp_s: float
    current_mA: float
    voltage_V: float
    implementation: str
    data_origin: str
    run_id: str = "unspecified"
    phase: str = "unspecified"


@dataclass(frozen=True)
class PhaseMetrics:
    phase: str
    duration_s: float
    mean_current_mA: float
    mean_power_mW: float


@dataclass(frozen=True)
class Metrics:
    duration_s: float
    mean_current_mA: float
    mean_power_mW: float
    peak_current_mA: float
    charge_mAh: float
    energy_mWh: float
    energy_per_cycle_mJ: float
    charge_per_cycle_uAh: float
    autonomy_h_ideal: float | None
    phase_metrics: tuple[PhaseMetrics, ...]


def _finite_float(value: str, field: str, line_number: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"line {line_number}: invalid {field}: {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"line {line_number}: {field} must be finite")
    return number


def load_samples(path: Path) -> list[Sample]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV is empty or has no header")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError("CSV missing required columns: " + ", ".join(sorted(missing)))

        samples: list[Sample] = []
        for line_number, row in enumerate(reader, start=2):
            if not row or all(value is None or value.strip() == "" for value in row.values()):
                continue
            implementation = (row.get("implementation") or "").strip()
            origin = (row.get("data_origin") or "").strip().upper()
            if not implementation:
                raise ValueError(f"line {line_number}: implementation is required")
            if origin not in VALID_ORIGINS:
                raise ValueError(
                    f"line {line_number}: data_origin must be MEASURED or SIMULATED"
                )
            timestamp = _finite_float(row.get("timestamp_s", ""), "timestamp_s", line_number)
            current = _finite_float(row.get("current_mA", ""), "current_mA", line_number)
            voltage = _finite_float(row.get("voltage_V", ""), "voltage_V", line_number)
            if current < 0:
                raise ValueError(f"line {line_number}: current_mA cannot be negative")
            if voltage <= 0:
                raise ValueError(f"line {line_number}: voltage_V must be positive")
            run_id = (row.get("run_id") or "unspecified").strip() or "unspecified"
            phase = (row.get("phase") or "unspecified").strip() or "unspecified"
            samples.append(Sample(timestamp, current, voltage, implementation, origin, run_id, phase))

    if not samples:
        raise ValueError("CSV contains no data rows")
    return samples


def calculate_metrics(samples: Iterable[Sample], capacity_mah: float | None,
                      period_s: float) -> Metrics:
    ordered = list(samples)
    if len(ordered) < 2:
        raise ValueError("at least two samples are required per implementation/origin")

    # Duplicate or decreasing timestamps make numerical integration ambiguous.
    for previous, current in zip(ordered, ordered[1:]):
        if current.timestamp_s <= previous.timestamp_s:
            raise ValueError("timestamps must be strictly increasing within each group")

    duration_s = ordered[-1].timestamp_s - ordered[0].timestamp_s
    current_area_mA_s = 0.0
    energy_area_mW_s = 0.0

    for left, right in zip(ordered, ordered[1:]):
        dt = right.timestamp_s - left.timestamp_s
        current_area_mA_s += (left.current_mA + right.current_mA) * 0.5 * dt
        left_power = left.current_mA * left.voltage_V
        right_power = right.current_mA * right.voltage_V
        energy_area_mW_s += (left_power + right_power) * 0.5 * dt

    mean_current = current_area_mA_s / duration_s
    mean_power = energy_area_mW_s / duration_s
    charge_mah = current_area_mA_s / 3600.0
    energy_mwh = energy_area_mW_s / 3600.0
    autonomy = None if capacity_mah is None or mean_current <= 0 else capacity_mah / mean_current

    # Attribute an interval to a phase only when both endpoint samples agree.
    # A phase transition interval is kept separate rather than guessed.
    phase_accumulator: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
    for left, right in zip(ordered, ordered[1:]):
        dt = right.timestamp_s - left.timestamp_s
        phase = left.phase if left.phase == right.phase else "TRANSITION"
        acc = phase_accumulator[phase]
        acc[0] += dt
        acc[1] += (left.current_mA + right.current_mA) * 0.5 * dt
        acc[2] += (left.current_mA * left.voltage_V + right.current_mA * right.voltage_V) * 0.5 * dt

    phase_metrics = tuple(
        PhaseMetrics(phase, values[0], values[1] / values[0], values[2] / values[0])
        for phase, values in sorted(phase_accumulator.items()) if values[0] > 0
    )

    return Metrics(
        duration_s=duration_s,
        mean_current_mA=mean_current,
        mean_power_mW=mean_power,
        peak_current_mA=max(sample.current_mA for sample in ordered),
        charge_mAh=charge_mah,
        energy_mWh=energy_mwh,
        energy_per_cycle_mJ=mean_power * period_s,
        charge_per_cycle_uAh=(mean_current * period_s / 3600.0) * 1000.0,
        autonomy_h_ideal=autonomy,
        phase_metrics=phase_metrics,
    )


def analyze(path: Path, capacity_mah: float | None, period_s: float) -> list[tuple[str, str, str, Metrics]]:
    groups: dict[tuple[str, str, str], list[Sample]] = defaultdict(list)
    for sample in load_samples(path):
        groups[(sample.implementation, sample.data_origin, sample.run_id)].append(sample)

    results = []
    for (implementation, origin, run_id), samples in sorted(groups.items()):
        results.append((implementation, origin, run_id,
                        calculate_metrics(samples, capacity_mah, period_s)))
    return results


def render_report(results: list[tuple[str, str, str, Metrics]], capacity_mah: float | None,
                  period_s: float) -> str:
    lines = [
        "# Power analysis results",
        "",
        f"- Period used for per-cycle estimates: {period_s:g} s",
        f"- Battery capacity: {capacity_mah:g} mAh" if capacity_mah is not None
        else "- Battery capacity: not supplied (autonomy omitted)",
        "",
        "| Implementation | Data origin | Run ID | Window (s) | Mean current (mA) | Peak sampled current (mA) | Mean power (mW) | Energy/cycle (mJ) | Charge/cycle (µAh) | Ideal autonomy (h) |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for implementation, origin, run_id, metric in results:
        autonomy = "n/a" if metric.autonomy_h_ideal is None else f"{metric.autonomy_h_ideal:.3f}"
        lines.append(
            f"| {implementation} | {origin} | {run_id} | {metric.duration_s:.3f} | "
            f"{metric.mean_current_mA:.6f} | {metric.peak_current_mA:.6f} | "
            f"{metric.mean_power_mW:.6f} | {metric.energy_per_cycle_mJ:.6f} | {metric.charge_per_cycle_uAh:.6f} | {autonomy} |"
        )
    lines.extend([
        "",
        "## Phase-level current summary",
        "",
        "| Implementation | Run ID | Phase | Duration (s) | Mean current (mA) | Mean power (mW) |",
        "|---|---|---|---:|---:|---:|",
    ])
    for implementation, _origin, run_id, metric in results:
        for phase_metric in metric.phase_metrics:
            lines.append(
                f"| {implementation} | {run_id} | {phase_metric.phase} | "
                f"{phase_metric.duration_s:.3f} | {phase_metric.mean_current_mA:.6f} | "
                f"{phase_metric.mean_power_mW:.6f} |"
            )
    lines.extend([
        "",
        "Intervals whose endpoint samples have different phase labels are reported as `TRANSITION`; "
        "they are not silently assigned to active or idle.",
        "",
        "> Energy and charge values are trapezoidal estimates from the supplied samples. "
        "Autonomy is an idealized capacity/current calculation, not a battery-life guarantee.",
        "",
    ])
    if any(origin == "SIMULATED" for _, origin, _, _ in results):
        lines.insert(1, "> **WARNING: this report includes SIMULATED data. It is not a physical measurement.**")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Input CSV file")
    parser.add_argument("--capacity-mah", type=float, default=None,
                        help="Rated battery capacity in mAh (optional)")
    parser.add_argument("--period-s", type=float, default=5.0,
                        help="Scenario period in seconds for per-cycle estimates (default: 5)")
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional path to write the Markdown report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.capacity_mah is not None and args.capacity_mah <= 0:
        print("error: --capacity-mah must be positive", file=sys.stderr)
        return 2
    if args.period_s <= 0:
        print("error: --period-s must be positive", file=sys.stderr)
        return 2
    try:
        results = analyze(args.input, args.capacity_mah, args.period_s)
        report = render_report(results, args.capacity_mah, args.period_s)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(report)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
