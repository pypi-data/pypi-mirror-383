# src/pvvoltloss/config.py
#####################################################################################
# OPV Voltage Loss Package
#
# Configuration module: configuration dataclass and default/example presets. 
# Author: Jolanda S Müller, Imperial College London
# Copyright (c) 2025, Imperial College London, BSD 3-Clause License
# Date: October 2025
#####################################################################################

from dataclasses import dataclass, fields, is_dataclass, replace
from importlib.resources import files
from pathlib import Path

# Copyright (c) 2025, Imperial College London, BSD 3-Clause License

@dataclass
class Config:
    eqe: str | None = None
    el: str | None = None
    voc: float | None = None
    eqe_columns: tuple[int,int] | None = None
    el_columns:  tuple[int,int] | None = None
    fit_range:   tuple[float,float] | None = None
    int_range:   tuple[float,float] | None = None
    out: Path | None = None
    device: str | None = None 
    choice: str | None = None 

    @staticmethod
    def get_defaults():
        return Config(
            voc=0.85,
            eqe_columns=(0,1),
            el_columns=(0,1),
            fit_range=(1.3,1.4),
            int_range=(0.8,3.0),
            out="results/voltage_losses.csv",
            device="sample",
            choice="append",
    )

    @staticmethod
    def get_example():
        root = files("pvvoltloss.data.examples")
        return  Config(
            eqe = str(root.joinpath("example_EQE.csv")),
            el = str(root.joinpath("example_EL.csv")),
            voc = 0.916,
            fit_range=(1.32, 1.41),
            int_range=(0.95, 3.0),
            eqe_columns=(0,2),
            el_columns=(0,1),
            device="Example Device"
        )

def layer_configs(*configs, ignore_none=True):
    """
    Layer multiple dataclass instances of the same class.
    Leftmost is the base. Later instances override earlier ones.
    If ignore_none=True, None values do not overwrite.
    """
    configs = [c for c in configs if c is not None]

    if not configs:
        raise ValueError("provide at least one dataclass instance")
    if not all(is_dataclass(c) for c in configs):
        raise TypeError("all arguments must be dataclass instances")

    cls = type(configs[0])
    if any(type(c) is not cls for c in configs):
        raise TypeError("all dataclasses must be the same class")

    names = {f.name for f in fields(cls)}
    result = configs[0]

    for cfg in configs[1:]:
        updates = {n: getattr(cfg, n) for n in names}
        if ignore_none:
            updates = {k: v for k, v in updates.items() if v is not None}
        result = replace(result, **updates)

    return result
