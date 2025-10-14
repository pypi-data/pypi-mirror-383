# src/pvvoltloss/nogui.py
#####################################################################################
# OPV Voltage Loss Package
#
# No-GUI Module: voltage loss analysis without user interface.
# Author: Jolanda S Müller, Imperial College 
# Copyright (c) 2025, Imperial College London, BSD 3-Clause License
# Date: October 2025
#####################################################################################

from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from . import physics
from .data_handler import export_voltage_losses, export_spectra_columns, import_data, export_figure
from .plotting import update_plot
import matplotlib.pyplot as plt
from . import Config

def run_headless(config: Config) -> pd.DataFrame:
    """Headless voltage-loss analysis: loads data, computes losses, exports results."""

    eqe_path = Path(config.eqe).expanduser().resolve()
    el_path  = Path(config.el).expanduser().resolve()
    voc = config.voc
    eqe_columns = config.eqe_columns
    el_columns = config.el_columns
    fit_range = config.fit_range
    int_range = config.int_range
    device = config.device
    out = config.out
    choice = config.choice

    if not eqe_path.is_file():
        print(f"EQE file not found: {eqe_path}")
        return
    if not el_path.is_file():
        print(f"EL file not found: {el_path}")
        return

    eqe, _ = import_data(file_path=eqe_path, columns=eqe_columns)
    el, _  = import_data(file_path=el_path, columns=el_columns)

    print("---STARTING VOLTAGE LOSS ANALYSIS---------------------------------------------------------")
    print("Running headless voltage-loss analysis.")
    print(f"- Loaded EQE from {eqe_path.name} columns {eqe_columns}, EL from {el_path.name} columns {el_columns}")
    print(f"- Device Voc={voc:.3f} V")
    print(f"- Using fit range: {fit_range}, Integration range: {int_range}")

    results, spectra = physics.calculate_voltage_losses(
        eqe_spectrum=eqe,
        el_spectrum=el,
        voc_device=float(voc),
        integration_range=int_range,
        fit_range=fit_range,
    )

    outspectra = Path(f"{device}")

    print(f"- Exporting results to ./{out}, and spectra to ./results/{outspectra}.csv")
    print("---RESULTS--------------------------------------------------------------------------------")

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    export_voltage_losses(device_name=device, df=results, choice=choice, gui_mode=False)
    outspectra.parent.mkdir(parents=True, exist_ok=True)
    export_spectra_columns(filename=str(outspectra), spectra=spectra, gui_mode=False)

    # print to stdout
    pd.set_option("display.max_columns", None)
    print(results.to_string(index=False))
    

    # make and save plot
    if True:
        fig, ax = plt.subplots(1, 1)

        # Rebuild all arrays from spectra
        eqe_spectrum = spectra["eqe_dev"]
        el_spectrum = spectra["el"]
        eqe_el = spectra["eqe_el"]
        eqe_derivative = spectra["eqe_derivative"]

        # Plot and save
        update_plot(
            ax=ax,
            eqe_spectrum=eqe_spectrum,
            el_spectrum=el_spectrum,
            eqe_el=eqe_el,
            eqe_derivative=eqe_derivative,
            results=results,
            fit_low=fit_range[0],
            fit_high=fit_range[1],
            int_low=int_range[0],
            int_high=int_range[1],
            device_name=device
        )
        export_figure(fig, name=device, dimensions=(14,11), gui_mode=False)
        plt.close(fig)
        print("---END---------------------------------------------------------------------------------------")

    return results