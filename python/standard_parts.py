"""Standard part selector for use in EngineeringPapyr code cells.

Usage in a code cell:
    from standard_parts import std_res_01, std_res_1, std_cap, std_ind
    from standard_parts import select_nearest, select_up, select_down

    R_calc = 4870  # calculated value in ohms
    R_std = select_nearest(R_calc, std_res_01)   # nearest standard value
    R_up  = select_up(R_calc, std_res_01)         # next value >= target
    R_down = select_down(R_calc, std_res_01)      # next value <= target
"""

import csv
from bisect import bisect_left, bisect_right
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent


def _load_csv(filename: str) -> list[float]:
    path = _BASE / filename
    if not path.exists():
        return []
    vals = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            for cell in row:
                cell = cell.strip()
                if cell:
                    try:
                        v = float(cell)
                        if v > 0:
                            vals.append(v)
                    except ValueError:
                        pass
    return sorted(vals)


std_res_01: list[float] = _load_csv('RES0.1.csv')
std_res_1: list[float] = _load_csv('RES1.0.csv')
std_cap: list[float] = _load_csv('CAP.csv')
std_ind: list[float] = _load_csv('IND.csv')


def select_nearest(target: float, std_values: list[float]) -> float:
    """Find the standard value closest to target."""
    if not std_values:
        return target
    idx = bisect_left(std_values, target)
    if idx == 0:
        return std_values[0]
    if idx >= len(std_values):
        return std_values[-1]
    below = std_values[idx - 1]
    above = std_values[idx]
    return below if (target - below) <= (above - target) else above


def select_up(target: float, std_values: list[float]) -> float:
    """Find the smallest standard value >= target."""
    if not std_values:
        return target
    idx = bisect_left(std_values, target * 0.9999)
    if idx >= len(std_values):
        return std_values[-1]
    return std_values[idx]


def select_down(target: float, std_values: list[float]) -> float:
    """Find the largest standard value <= target."""
    if not std_values:
        return target
    idx = bisect_right(std_values, target * 1.0001) - 1
    if idx < 0:
        return std_values[0]
    return std_values[idx]
