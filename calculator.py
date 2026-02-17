#!/usr/bin/env python3
"""Single-file sizing calculator for Rectifiers, 1PH, and 3PH battery chargers.

Designed to be packaged as a single executable with:
    pyinstaller --onefile calculator.py
"""

from __future__ import annotations

import argparse
import json
import math

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

    return Result("rectifier", kva, ipri, isec, vsec_ln, vsec_ll, cb_primary, cb_secondary, cb_dc, wire_primary, wire_secondary, wire_dc, heat_kw, heat_btu, cfm)


def calc_1ph(inp: Inputs) -> Result:
    isec = 1.11 * (1 + inp.line_fluct_pct / 100.0) * (inp.vdc * inp.idc)

    return Result("charger_1ph", kva, ipri, iac_out, inp.vdc, None, cb_primary, cb_secondary, cb_dc, wire_primary, wire_secondary, wire_dc, heat_kw, heat_btu, cfm)


def calc_3ph(inp: Inputs) -> Result:
    vsec_ln = 0.428 * (1 + inp.line_fluct_pct / 100.0) * inp.vdc + (2 if inp.vdc < 87 else 0)
    vsec_ll = math.sqrt(3) * vsec_ln
    isec = (1 + inp.sec_current_safety_pct / 100.0) * inp.idc * 0.83
    kva = kv_round_3ph(vsec_ll * isec * math.sqrt(3) / 1000.0)
    ipri = kva * 1000.0 / inp.vpri / math.sqrt(3)



if __name__ == "__main__":
    raise SystemExit(main())
