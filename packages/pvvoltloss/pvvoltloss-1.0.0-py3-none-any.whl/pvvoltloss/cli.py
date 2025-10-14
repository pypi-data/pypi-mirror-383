# src/pvvoltloss/cli.py
#####################################################################################
# OPV Voltage Loss Package
#
# Command Line Interface: Entry point parsing command line keywords
# Author: Jolanda S Müller, Imperial College London
# Copyright (c) 2025, Imperial College London, BSD 3-Clause License
# Date: October 2025
#####################################################################################

from __future__ import annotations
from pvvoltloss import __version__
import argparse
from pathlib import Path
from . import run  # this is from __init__

def build_parser():
    p = argparse.ArgumentParser(
        prog="pvvoltloss",
        description="PV voltage-loss analysis",
        argument_default=argparse.SUPPRESS,
    )
    p.add_argument("--nogui",   action="store_true", help="Run headless CLI workflow. Requires --eqe, --el, --voc; OR --example.")
    p.add_argument("--example", action="store_true", help="Run with example data; individual params can still be overridden.")
    p.add_argument("--eqe",      type=Path, help="Path to EQE file")
    p.add_argument("--el",       type=Path, help="Path to EL file")
    p.add_argument("--voc",      type=float, help="Open-circuit voltage (V)")
    p.add_argument("--eqe_columns", type=_parse_cols, help="EQE columns (e.g. 0:1)")
    p.add_argument("--el_columns",  type=_parse_cols, help="EL columns (e.g. 0:1)")
    p.add_argument("--fit_range",      type=_parse_range, help="Fitting range (eV), e.g. 1.30:1.40")
    p.add_argument("--int_range",   type=_parse_range, help="Integration range (eV), e.g. 0.8:3.0")
    p.add_argument("--out",      type=Path, help="Output CSV (default results/voltage_losses.csv)")
    p.add_argument("--device",   type=str, help="Device name")
    p.add_argument("--version",  action="version", version=f"%(prog)s v{__version__}")
    return p

def _parse_range(s: str) -> tuple[float, float]:
    a, b = s.split(":")
    return float(a), float(b)

def _parse_cols(s: str) -> tuple[int, int]:
    a, b = s.split(":")
    return int(a), int(b)

def parse(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    user_config = vars(args)
    return user_config

def main(argv=None):
    """Read and parse command line input keywords, and run accordingly."""

    user_config = parse(argv)

    mode = "nogui" if user_config.get("nogui") else "gui"
    example = True if user_config.get("example") else False
    user_config.pop("nogui", None)
    user_config.pop("example", None)

    # run in appropriate mode
    run(mode=mode, example=example, **user_config)

