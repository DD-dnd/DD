#!/usr/bin/env python3
"""Single-file sizing calculator for Rectifiers, 1PH, and 3PH battery chargers.

Designed to be packaged as a single executable with:
    pyinstaller --onefile calculator.py
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from typing import List, Tuple

CB_TABLE: List[Tuple[float, str]] = [
    (1.004 * 0, "Check"), (1.004 * 1, "5"), (5, "10"), (10, "15"), (15, "20"),
    (20, "25"), (25, "30"), (1.004 * 30, "40"), (40, "50"), (50, "60"),
    (60, "60"), (63, "70"), (70, "80"), (80, "90"), (90, "100"),
    (100, "110"), (110, "125"), (125, "150"), (150, "175"), (175, "200"),
    (200, "225"), (225, "250"), (250, "300"), (300, "350"), (350, "400"),
    (400, "450"), (450, "500"), (500, "600"), (600, "700"), (700, "800"),
    (800, "900"), (900, "1000"), (1000, "1200"),
]

WIRE_TABLE: List[Tuple[float, str]] = [
    (1.004 * 0, "#10"), (1.004 * 4, "#10"), (6, "#10"), (9, "#10"), (15, "#10"),
    (22, "#10"), (40, "#8"), (60, "#6"), (80, "#4"), (105, "#3"), (120, "#2"),
    (140, "#1"), (165, "#1/0"), (195, "#2/0"), (225, "#3/0"), (260, "#4/0"),
    (300, "250MCM"), (340, "300MCM"), (375, "#2/0 2x"), (432, "#3/0 2x"),
    (499.2, "#4/0 2x"), (576, "250MCM 2x"), (652.8, "300MCM 2x"), (720, "Buss"),
]


def lookup_last_leq(value: float, table: List[Tuple[float, str]]) -> str:
    result = table[0][1]
    for key, mapped in table:
        if value >= key:
            result = mapped
        else:
            break
    return result


def ceiling(value: float, significance: float) -> float:
    return math.ceil(value / significance) * significance


def kv_round_3ph(raw_kva: float) -> float:
    if ceiling(raw_kva, 0.25) < 10:
        return ceiling(raw_kva, 0.25)
    if ceiling(raw_kva, 0.25) < 20:
        return ceiling(raw_kva, 0.5)
    return ceiling(raw_kva, 1)


@dataclass
class Inputs:
    vdc: float
    idc: float
    vpri: float
    line_fluct_pct: float = 5
    sec_current_safety_pct: float = 20
    cb_primary_safety_pct: float = 30
    cb_secondary_safety_pct: float = 30
    cb_dc_safety_pct: float = 20
    wire_primary_safety_pct: float = 15
    wire_secondary_safety_pct: float = 10
    wire_dc_safety_pct: float = 10
    ambient_c: float = 40
    inside_c: float = 55
    airflow_safety_pct: float = 20


@dataclass
class Result:
    family: str
    kva: float
    i_primary_a: float
    i_secondary_a: float
    v_secondary_ln_v: float
    v_secondary_ll_v: float | None
    cb_primary: str
    cb_secondary: str
    cb_dc: str
    wire_primary: str
    wire_secondary: str
    wire_dc: str
    heat_kw: float
    heat_btu_h: float
    required_cfm: float


def calc_rectifier(inp: Inputs) -> Result:
    vsec_ln = 0.428 * (1 + inp.line_fluct_pct / 100.0) * inp.vdc + (2 if inp.vdc < 85 else 0)
    vsec_ll = math.sqrt(3) * vsec_ln
    isec = (1 + inp.sec_current_safety_pct / 100.0) * inp.idc * 0.83
    kva = kv_round_3ph(vsec_ll * isec * math.sqrt(3) / 1000.0)
    ipri = kva * 1000.0 / inp.vpri / math.sqrt(3)
    cb_primary = lookup_last_leq((1 + inp.cb_primary_safety_pct / 100.0) * ipri, CB_TABLE)
    cb_secondary = lookup_last_leq((1 + inp.cb_secondary_safety_pct / 100.0) * isec, CB_TABLE)
    cb_dc = lookup_last_leq((1 + inp.cb_dc_safety_pct / 100.0) * inp.idc, CB_TABLE)
    wire_primary = lookup_last_leq((1 + inp.wire_primary_safety_pct / 100.0) * ipri, WIRE_TABLE)
    wire_secondary = lookup_last_leq((1 + inp.wire_secondary_safety_pct / 100.0) * isec, WIRE_TABLE)
    wire_dc = lookup_last_leq((1 + inp.wire_dc_safety_pct / 100.0) * inp.idc, WIRE_TABLE)
    heat_kw = (2 * inp.idc + 0.06 * kva * 1000.0) / 1000.0
    heat_btu = heat_kw * 3.412142 * 1000.0
    cfm = 1760 * heat_kw / max(inp.inside_c - inp.ambient_c, 0.1) * (1 + inp.airflow_safety_pct / 100.0)
    return Result("rectifier", kva, ipri, isec, vsec_ln, vsec_ll, cb_primary, cb_secondary, cb_dc, wire_primary, wire_secondary, wire_dc, heat_kw, heat_btu, cfm)


def calc_1ph(inp: Inputs) -> Result:
    isec = 1.11 * (1 + inp.line_fluct_pct / 100.0) * (inp.vdc * inp.idc)
    iac_out = (1 + inp.sec_current_safety_pct / 100.0) * inp.vpri * 1.11
    kva = ceiling(isec * iac_out / 1000.0, 0.25)
    ipri = kva * 1000.0 / inp.vpri
    cb_primary = lookup_last_leq((1 + inp.cb_primary_safety_pct / 100.0) * ipri, CB_TABLE)
    cb_secondary = lookup_last_leq((1 + inp.cb_secondary_safety_pct / 100.0) * iac_out, CB_TABLE)
    cb_dc = lookup_last_leq((1 + inp.cb_dc_safety_pct / 100.0) * inp.vpri, CB_TABLE)
    wire_primary = lookup_last_leq((1 + inp.wire_primary_safety_pct / 100.0) * ipri, WIRE_TABLE)
    wire_secondary = lookup_last_leq((1 + inp.wire_secondary_safety_pct / 100.0) * iac_out, WIRE_TABLE)
    wire_dc = lookup_last_leq((1 + inp.wire_dc_safety_pct / 100.0) * inp.vpri, WIRE_TABLE)
    heat_kw = (2 * inp.vpri + 0.05 * kva * 1000.0) / 1000.0
    heat_btu = heat_kw * 3.412142 * 1000.0
    cfm = 1760 * heat_kw / max(inp.inside_c - inp.ambient_c, 0.1) * (1 + inp.airflow_safety_pct / 100.0)
    return Result("charger_1ph", kva, ipri, iac_out, inp.vdc, None, cb_primary, cb_secondary, cb_dc, wire_primary, wire_secondary, wire_dc, heat_kw, heat_btu, cfm)


def calc_3ph(inp: Inputs) -> Result:
    vsec_ln = 0.428 * (1 + inp.line_fluct_pct / 100.0) * inp.vdc + (2 if inp.vdc < 87 else 0)
    vsec_ll = math.sqrt(3) * vsec_ln
    isec = (1 + inp.sec_current_safety_pct / 100.0) * inp.idc * 0.83
    kva = kv_round_3ph(vsec_ll * isec * math.sqrt(3) / 1000.0)
    ipri = kva * 1000.0 / inp.vpri / math.sqrt(3)
    cb_primary = lookup_last_leq((1 + inp.cb_primary_safety_pct / 100.0) * ipri, CB_TABLE)
    cb_secondary = lookup_last_leq((1 + inp.cb_secondary_safety_pct / 100.0) * isec, CB_TABLE)
    cb_dc = lookup_last_leq((1 + inp.cb_dc_safety_pct / 100.0) * inp.idc, CB_TABLE)
    wire_primary = lookup_last_leq((1 + inp.wire_primary_safety_pct / 100.0) * ipri, WIRE_TABLE)
    wire_secondary = lookup_last_leq((1 + inp.wire_secondary_safety_pct / 100.0) * isec, WIRE_TABLE)
    wire_dc = lookup_last_leq((1 + inp.wire_dc_safety_pct / 100.0) * inp.idc, WIRE_TABLE)
    heat_kw = (2 * inp.idc + 0.07 * kva * 1000.0) / 1000.0
    heat_btu = heat_kw * 3.412142 * 1000.0
    cfm = 1760 * heat_kw / max(inp.inside_c - inp.ambient_c, 0.1) * (1 + inp.airflow_safety_pct / 100.0)
    return Result("charger_3ph", kva, ipri, isec, vsec_ln, vsec_ll, cb_primary, cb_secondary, cb_dc, wire_primary, wire_secondary, wire_dc, heat_kw, heat_btu, cfm)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Sizing calculator (single-file EXE friendly)")
    p.add_argument("family", nargs="?", choices=["rectifier", "1ph", "3ph"], help="Product family")
    p.add_argument("--vdc", type=float)
    p.add_argument("--idc", type=float)
    p.add_argument("--vpri", type=float)
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.add_argument("--interactive", action="store_true", help="Prompt for inputs interactively")
    return p


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def run_calculation(family: str, inp: Inputs) -> Result:
    if family == "rectifier":
        return calc_rectifier(inp)
    if family == "1ph":
        return calc_1ph(inp)
    return calc_3ph(inp)


def prompt_user() -> tuple[str, Inputs]:
    print("No CLI arguments detected. Starting interactive mode...\n")
    family = input("Family [rectifier/1ph/3ph]: ").strip().lower()
    if family not in {"rectifier", "1ph", "3ph"}:
        raise ValueError("family must be rectifier, 1ph, or 3ph")
    vdc = float(input("Vdc: ").strip())
    idc = float(input("Idc: ").strip())
    vpri = float(input("Vpri: ").strip())
    return family, Inputs(vdc=vdc, idc=idc, vpri=vpri)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        if args.interactive or len(sys.argv) == 1:
            family, inp = prompt_user()
        else:
            missing = [n for n in ["family", "vdc", "idc", "vpri"] if getattr(args, n) is None]
            if missing:
                build_parser().print_usage()
                print(f"error: missing required arguments: {', '.join(missing)}")
                print("example: calculator.exe rectifier --vdc 600 --idc 600 --vpri 480 --json")
                return 2
            family = args.family
            inp = Inputs(vdc=args.vdc, idc=args.idc, vpri=args.vpri)

        result = run_calculation(family, inp)
        if args.json:
            print(json.dumps(asdict(result), indent=2))
        else:
            for k, v in asdict(result).items():
                print(f"{k}: {v}")
        return 0
    except ValueError as exc:
        print(f"input error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
