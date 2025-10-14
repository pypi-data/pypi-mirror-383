# src/pvvoltloss/plotting.py
#####################################################################################
# OPV Voltage Loss Package
#
# Plotting Module: Function for plotting the EQE EL fit and the EQE derivative.
# Author: Jolanda S Müller, Imperial College London
# Copyright (c) 2025, Imperial College London, BSD 3-Clause License
# Date: October 2025
#####################################################################################

import numpy as np
import matplotlib.pyplot as plt

LIGHT_COLOR = "#98ddea"
MEDIUM_COLOR = "#238a9c"
GREY_COLOR = "#657274"
DARK_COLOR = "#082b31"

def update_plot(
    ax,
    eqe_spectrum,
    el_spectrum,
    eqe_el,
    eqe_derivative,
    results,
    fit_low,
    fit_high,
    int_low,
    int_high,
    device_name
):
    """
    Update the given matplotlib axes with EQE/EL data and derivative inset.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Main axes to plot into.
    eqe_spectrum : ndarray (Nx2)
        Device EQE spectrum (energy [eV], EQE).
    el_spectrum : ndarray (Nx2)
        Raw EL spectrum (unused in this plot but validated for completeness).
    eqe_el : ndarray (Nx2)
        EL-derived EQE.
    eqe_derivative : ndarray (Nx2)
        d(EQE)/dE data for inset.
    results : pandas.DataFrame
        DataFrame containing at least column "Eg (eV)".
    fit_low, fit_high : float
        Energy range used for fitting.
    int_low, int_high : float
        Integration limits.
    """

    # --- Check Data Validity
    if eqe_spectrum is None or el_spectrum is None:
        return
    if eqe_spectrum.size == 0 or el_spectrum.size == 0:
        return
    if eqe_el is None or eqe_derivative is None:
        return

    # --- Main plot setup
    ax.cla()
    ax.set_yscale("log")
    ax.set_ylim(1e-13, 1e3)
    ax.set_xlim(0.5, 3.5)
    ax.set_xlabel(r"Energy $E$ (eV)", fontsize=9)
    ax.set_ylabel(r"$\mathrm{EQE}(E)$", fontsize=9)
    ax.tick_params(axis="both", which="major", labelsize=8)
    ax.text(0.97, 0.97, device_name, transform=ax.transAxes, fontsize=10, fontweight="bold", ha="right", va="top")

    # --- Plot EQE (device)
    ax.plot(
        eqe_spectrum[:, 0],
        eqe_spectrum[:, 1],
        "o",
        color=LIGHT_COLOR,
        label=r"$EQE_\text{device}$",
    )

    # --- Fit range points
    mask_fit = (eqe_spectrum[:, 0] >= fit_low) & (eqe_spectrum[:, 0] <= fit_high)
    if np.any(mask_fit):
        ax.plot(
            eqe_spectrum[mask_fit, 0],
            eqe_spectrum[mask_fit, 1],
            "o",
            color=MEDIUM_COLOR,
            label="Fitting range",
        )

    # --- EL-derived EQE (mask x ≤ 1.8 eV)
    mask = eqe_el[:, 0] <= 1.8
    ax.plot(
        eqe_el[mask, 0],
        eqe_el[mask, 1],
        "--",
        color=DARK_COLOR,
        label=r"$EQE_\text{EL}$",
    )

    # --- Integration range vertical lines
    ax.axvline(int_low, color=GREY_COLOR, linestyle=":", linewidth=1.5, label="Integr. range")
    ax.axvline(int_high, color=GREY_COLOR, linestyle=":", linewidth=1.5)

    # --- Legend (bottom center anchor)
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.02),
        bbox_transform=ax.transAxes,
        ncol=2,
        frameon=False,
        fontsize=9,
    )

    # --- Inset axes for derivative
    inset_ax = ax.inset_axes([0.38, 0.05, 0.6, 0.5])  # [x0, y0, width, height]
    inset_ax.plot(eqe_derivative[:, 0], eqe_derivative[:, 1], "-", color=DARK_COLOR)
    inset_ax.tick_params(
        axis="x",
        top=True,
        labeltop=True,
        bottom=False,
        labelbottom=False,
        which="major",
        labelsize=8,
    )
    inset_ax.tick_params(axis="y", which="both", left=False, right=False, labelleft=False)
    inset_ax.xaxis.set_label_position("top")
    inset_ax.set_xlabel(r"Energy $E$ (eV)", fontsize=9)
    inset_ax.set_ylabel(r"d$EQE$/d$E$ (a.u.)", fontsize=9)
    inset_ax.set_yscale("linear")

    # --- Vertical line for Egap
    egap = results.iloc[0]["Eg (eV)"]
    inset_ax.axvline(egap, color=MEDIUM_COLOR, linestyle="--", linewidth=1)
    inset_ax.text(
        egap * 1.05,
        inset_ax.get_ylim()[1] * 0.90,
        rf"$E_\text{{gap}} = {egap:.2f}\,\mathrm{{eV}}$",
        color=MEDIUM_COLOR,
        fontsize=9,
        ha="left",
        va="top",
        alpha=0.7,
    )

    return ax
