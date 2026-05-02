"""Electronic Part Stress Analysis (EPSA) for EngineeringPapyr code cells.

All inputs must be in SI base units: Amps, Volts, Ohms, Farads.
Math cells with units (e.g. "0.42 [mA]") auto-convert to SI before
reaching the code cell. If entering raw numbers without units,
use SI values directly (e.g. 0.42e-3 for 0.42 mA).

Derating defaults: VOLTAGE_DERATING = 0.80, POWER_DERATING = 0.60.
To customize, set them before calling resistor()/capacitor():

    import part_stress
    part_stress.VOLTAGE_DERATING = 0.70
    part_stress.POWER_DERATING = 0.50

Usage in a code cell (function signature: EPSA(I_{R1}, I_{R2}, V_{Cin}) = [text]):

    from part_stress import resistor, capacitor, stress_report

    def calculate(i_r1, i_r2, v_cin):
        return stress_report(
            resistor("R1", 10e3, "1%", i_r1),
            resistor("R2", 4.7e3, "1%", i_r2),
            capacitor("C_IN", 100e-9, "10%", v_cin),
        )
"""

import csv
import math
from dataclasses import dataclass
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent

VOLTAGE_DERATING = 0.80
POWER_DERATING = 0.60

STD_CAP_VOLTAGES = [4, 6.3, 10, 16, 25, 35, 50, 100, 200, 250, 500, 630, 1000, 2000, 3000]


@dataclass
class StressCheck:
    parameter: str
    rated: float
    derating: float
    derated: float
    actual: float
    stress_pct: float
    status: str


@dataclass
class ComponentResult:
    ref: str
    comp_type: str
    package: str
    value: float
    tolerance: str
    checks: list[StressCheck]
    current: float | None = None


def _load_pkg_ratings() -> dict[tuple[str, str], dict[str, float]]:
    path = _BASE / 'PKG_RATINGS.csv'
    if not path.exists():
        return {}
    ratings: dict[tuple[str, str], dict[str, float]] = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            comp_type = row['comp_type'].strip()
            package = row['package'].strip()
            entry: dict[str, float] = {}
            if row.get('voltage', '').strip():
                entry['voltage'] = float(row['voltage'])
            if row.get('power', '').strip():
                entry['power'] = float(row['power'])
            ratings[(comp_type, package)] = entry
    return ratings


_PKG_RATINGS = _load_pkg_ratings()


def _packages_for(comp_type: str) -> list[tuple[str, dict[str, float]]]:
    return [
        (pkg, ratings)
        for (ct, pkg), ratings in _PKG_RATINGS.items()
        if ct == comp_type
    ]


def _select_cap_voltage(v_actual: float) -> float:
    v_needed = v_actual / VOLTAGE_DERATING
    for v in STD_CAP_VOLTAGES:
        if v >= v_needed:
            return v
    raise ValueError(
        f"No standard capacitor voltage rating can handle {v_actual:.3g}V "
        f"(need >= {v_needed:.3g}V after {VOLTAGE_DERATING:.0%} derating)"
    )


def _make_check(parameter: str, rated: float, derating: float, actual: float) -> StressCheck:
    derated = rated * derating
    stress_pct = abs(actual) / derated if derated > 0 else float('inf')
    status = "PASS" if stress_pct < 1.0 else "FAIL"
    return StressCheck(
        parameter=parameter,
        rated=rated,
        derating=derating,
        derated=derated,
        actual=abs(actual),
        stress_pct=round(stress_pct, 3),
        status=status,
    )


def resistor(ref: str, resistance: float, tolerance: str, current: float,
             *, package: str | None = None,
             v_rated: float | None = None,
             p_rated: float | None = None) -> ComponentResult:
    v_actual = abs(current) * resistance
    p_actual = current ** 2 * resistance

    if package is not None:
        key = ('resistor', package)
        pkg = _PKG_RATINGS.get(key, {})
        eff_p_rated = p_rated if p_rated is not None else pkg.get('power')
        eff_v_rated_pkg = v_rated if v_rated is not None else pkg.get('voltage')
        if eff_p_rated is None:
            raise ValueError(f"No power rating for resistor package '{package}'. Provide p_rated.")
        if eff_v_rated_pkg is None:
            raise ValueError(f"No voltage rating for resistor package '{package}'. Provide v_rated.")
        eff_v_rated = min(eff_v_rated_pkg, math.sqrt(eff_p_rated * resistance))
    else:
        selected_pkg = None
        for pkg_name, pkg_ratings in _packages_for('resistor'):
            pkg_p = p_rated if p_rated is not None else pkg_ratings.get('power')
            pkg_v = v_rated if v_rated is not None else pkg_ratings.get('voltage')
            if pkg_p is None or pkg_v is None:
                continue
            eff_v = min(pkg_v, math.sqrt(pkg_p * resistance))
            if pkg_p * POWER_DERATING >= p_actual and eff_v * VOLTAGE_DERATING >= v_actual:
                selected_pkg = pkg_name
                eff_p_rated = pkg_p
                eff_v_rated = eff_v
                break
        if selected_pkg is None:
            raise ValueError(
                f"No SMD package can handle resistor {ref} "
                f"(V={v_actual:.3g}V, P={p_actual:.3g}W). Specify a custom package."
            )
        package = selected_pkg

    checks = [
        _make_check("voltage", eff_v_rated, VOLTAGE_DERATING, v_actual),
        _make_check("power", eff_p_rated, POWER_DERATING, p_actual),
    ]
    return ComponentResult(
        ref=ref,
        comp_type="resistor",
        package=package,
        value=resistance,
        tolerance=tolerance,
        checks=checks,
        current=abs(current),
    )


def capacitor(ref: str, capacitance: float, tolerance: str, voltage: float,
              *, package: str | None = None,
              v_rated: float | None = None) -> ComponentResult:
    if v_rated is None:
        v_rated = _select_cap_voltage(abs(voltage))

    if package is not None:
        pkg = _PKG_RATINGS.get(('capacitor', package), {})
        pkg_max_v = pkg.get('voltage', float('inf'))
        if v_rated > pkg_max_v:
            raise ValueError(
                f"Capacitor package '{package}' only supports up to {pkg_max_v}V, "
                f"but selected voltage rating is {v_rated}V."
            )
    else:
        selected_pkg = None
        for pkg_name, pkg_ratings in _packages_for('capacitor'):
            pkg_max_v = pkg_ratings.get('voltage', 0)
            if pkg_max_v >= v_rated:
                selected_pkg = pkg_name
                break
        if selected_pkg is None:
            raise ValueError(
                f"No SMD package can handle capacitor {ref} "
                f"(V_rated={v_rated}V). Specify a custom package."
            )
        package = selected_pkg

    checks = [_make_check("voltage", v_rated, VOLTAGE_DERATING, abs(voltage))]
    return ComponentResult(
        ref=ref,
        comp_type="capacitor",
        package=package,
        value=capacitance,
        tolerance=tolerance,
        checks=checks,
    )


def _format_resistance(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:.4g}"


def _format_capacitance_pf(value: float) -> str:
    pf = value * 1e12
    if pf == int(pf):
        return str(int(pf))
    return f"{pf:.4g}"


def _get_check(comp: ComponentResult, parameter: str) -> StressCheck | None:
    for chk in comp.checks:
        if chk.parameter == parameter:
            return chk
    return None


def stress_report(*component_results: ComponentResult) -> str:
    resistors = [c for c in component_results if c.comp_type == "resistor"]
    capacitors = [c for c in component_results if c.comp_type == "capacitor"]
    others = [c for c in component_results if c.comp_type not in ("resistor", "capacitor")]

    sections = []

    if resistors:
        lines = ["Resistors"]
        lines.append("Ref,Package,Value(ohm),Tolerance,Current(mA),"
                      "V_rated(V),V_derated(V),V_actual(V),V_stress,V_status,"
                      "P_rated(mW),P_derated(mW),P_actual(mW),P_stress,P_status")
        for comp in resistors:
            val_str = _format_resistance(comp.value)
            i_ma = comp.current * 1e3 if comp.current is not None else 0
            v = _get_check(comp, "voltage")
            p = _get_check(comp, "power")
            lines.append(
                f"{comp.ref},{comp.package},{val_str},{comp.tolerance},{i_ma:.4g},"
                f"{v.rated:.4g},{v.derated:.4g},{v.actual:.4g},{v.stress_pct},{v.status},"
                f"{p.rated * 1e3:.4g},{p.derated * 1e3:.4g},{p.actual * 1e3:.4g},{p.stress_pct},{p.status}"
            )
        sections.append("\n".join(lines))

    if capacitors:
        lines = ["Capacitors"]
        lines.append("Ref,Package,Value(pF),Tolerance,"
                      "V_rated(V),V_derated(V),V_actual(V),V_stress,V_status")
        for comp in capacitors:
            val_str = _format_capacitance_pf(comp.value)
            v = _get_check(comp, "voltage")
            lines.append(
                f"{comp.ref},{comp.package},{val_str},{comp.tolerance},"
                f"{v.rated:.4g},{v.derated:.4g},{v.actual:.4g},{v.stress_pct},{v.status}"
            )
        sections.append("\n".join(lines))

    if others:
        lines = ["Other Components"]
        lines.append("Ref,Type,Package,Value,Tolerance,Parameter,Rated,Derated,Actual,Stress%,Status")
        for comp in others:
            val_str = _format_value(comp.comp_type, comp.value)
            for chk in comp.checks:
                lines.append(
                    f"{comp.ref},{comp.comp_type},{comp.package},{val_str},{comp.tolerance},"
                    f"{chk.parameter},{chk.rated:.4g},{chk.derated:.4g},"
                    f"{chk.actual:.4g},{chk.stress_pct},{chk.status}"
                )
        sections.append("\n".join(lines))

    return "\n\n".join(sections)
