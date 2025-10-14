# src/pvvoltloss/physics.py
#####################################################################################
# OPV Voltage Loss Package
#
# Physics Module: Holds all functions responsible for calculating the physics.
# Author: Jolanda S Müller, Imperial College London
# Copyright (c) 2025, Imperial College London, BSD 3-Clause License
# Date: October 2025
#####################################################################################

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import importlib.resources as resources
from importlib.resources import files
import pandas as pd

""" Physical Constants """
q  = 1.602176565e-19  # C
h  = 6.62606957e-34   # Js
kT = 0.026            # eV
c  = 29979245800      # cm/s

def load_solar_spectrum() -> NDArray[np.float64]:
    """
    Load the AM1.5G solar spectrum from the package data.
    Returns a 2D array with two columns: energy (eV) and photon flux (photons/(s cm² eV)).
    """
    # Load from package data
    solar_spectrum = np.loadtxt(resources.files("pvvoltloss") / "data" / "solarSpectrum.csv", delimiter="\t")
    return solar_spectrum

def black_body_radiation(energy):
    return 2 * np.pi * 1e3 * (q**2 / h**3 / c**2) * energy**2 * np.exp(-energy / kT)

def calculate_bandgap(eqe_spectrum: NDArray[np.float64], interp_factor = 5) -> float:
    """
    Calculate the photovoltaic bandgap Eg from the EQE spectrum using Rau's method.
    (U. Rau, et al., Phys. Rev. App. 7.4 (2017). DOI: 10.1103/PhysRevApplied.7.044016.)
    The method computes d(EQE)/dE and takes the energy centroid over the region where dEQE exceeds 0.5 * max(dEQE)`

    Parameters:
      eqe_spectrum : ndarray, shape (N, 2)    first column = photon energy in eV (E), second column = fractional EQE

    Returns:
      Eg_PV : float    Photovoltaic Bandgap in eV (np.nan if there are issues
    """
    eqe_spectrum = _sort_spectrum(eqe_spectrum)
    energy = eqe_spectrum[:,0]
    eqe    = eqe_spectrum[:,1]

    # Normalize, interpolate, and smooth
    eqe = eqe / np.max(eqe)
    energy, eqe = _interpolate(energy, eqe, interp_factor = interp_factor)
    eqe = _smooth(eqe, toggle=True)

    # Derivative
    dEQE = np.gradient(eqe, energy)

    # Get bandgap
    threshold = 0.5 * np.max(dEQE)
    mask = dEQE >= threshold
    if np.sum(mask) > 1:
        Eg_PV = np.sum(energy[mask] * dEQE[mask]) / np.sum(dEQE[mask])
    else:
        Eg_PV = np.nan

    eqe_derivative = np.column_stack((energy, dEQE))

    return Eg_PV, eqe_derivative

def _interpolate(x_raw, y_raw, interp_factor = 1):
    """
    Cubic-spline interpolation of (x_raw, y_raw).
    Returns interpolated values at a denser grid of length len(x_raw) * interp_factor.
    """
    x_min, x_max = np.min(x_raw), np.max(x_raw)
    x_interp = np.linspace(x_min, x_max, len(x_raw) * interp_factor)
    y_interp = interp1d(x_raw, y_raw, kind='cubic', fill_value="extrapolate")(x_interp)
    return x_interp, y_interp

def _smooth(curve, toggle=True):
    """
    Apply Savitzky-Golay smoothing to a 1D curve. Uses a window up to 31 points (or shorter if needed).
    Returns smoothed curve if toggle=True, or original curve if toggle=False
    """
    window_length = 31 if len(curve) >= 31 else len(curve) // 2 * 2 + 1
    if toggle == True:
        return savgol_filter(curve, window_length=window_length, polyorder=3)
    else:
        return curve

def _sort_spectrum(spectrum: NDArray[np.float64]) -> np.ndarray:
    x = spectrum[:,0]
    y = spectrum[:,1]
    order = np.argsort(x)
    return np.column_stack((x[order], y[order]))

def extend_eqe_reciprocity(eqe_dev_spectrum: NDArray[np.float64], el_spectrum: NDArray[np.float64], energy_fit_range = (1.0,4.0)) -> NDArray[np.float64]:
    """
    Extend EQE spectrum to lower energies via reciprocity with EL data.
    J. Yao, et al., Phys. Rev. App. 4.1 (2015), pp. 1-10. DOI: 10.1103/PhysRevApplied.4.014020.

    Parameters
    ----------
    > eqe_dev_spectrum : ndarray of shape (N, 2)      Device EQE(E) spectrum (energy [eV], EQE [fractional]).
    > el_spectrum : ndarray of shape (M, 2)           Electroluminescence spectrum (energy [eV], intensity).
    > energy_fit_range : tuple(float, float)         Energy range [e_min, e_max] used for scaling EL-derived EQE to device EQE.

    Returns:
        > ndarray of shape (K, 2)                     Extended EQE spectrum with energy in the first column and scaled EQE in the second column.
    """
    eqe_dev_spectrum = _sort_spectrum(eqe_dev_spectrum)
    el_spectrum = _sort_spectrum(el_spectrum)
    energy_el = el_spectrum[:,0]
    energy_eqe_dev = eqe_dev_spectrum[:,0]
    el  =  el_spectrum[:,1]
    eqe_dev = eqe_dev_spectrum[:,1]

    # Reciprocity (Yao et al., Eq. 5)
    phi_BB = black_body_radiation(energy_el)
    EQE_EL_reciprocity = el / phi_BB / (np.exp(1/kT) - 1)

    # Scale EQE_EL to match EQE_PV inside the chosen fit range
    fit_mask = (energy_fit_range[0] < energy_eqe_dev) & (energy_eqe_dev < energy_fit_range[1])
    interp_EL_on_PV = np.interp(energy_eqe_dev[fit_mask], energy_el, EQE_EL_reciprocity)
    scaling = np.mean(interp_EL_on_PV / eqe_dev[fit_mask])
    EQE_EL_fitted = EQE_EL_reciprocity / scaling

    # Combine EQE_dev and EQE_el, using EQE_EL (≤ mid‑point)   +   EQE_dev (≥ mid‑point)
    mid_E = np.mean(energy_fit_range)
    bottom_E = np.arange(energy_el.min(), mid_E, 0.001)
    top_E    = np.arange(mid_E, energy_eqe_dev.max()+0.001, 0.001)

    bottom_Q = np.interp(bottom_E, energy_el, EQE_EL_fitted)
    top_Q    = np.interp(top_E,    energy_eqe_dev, eqe_dev)

    Energy_combined = np.concatenate((bottom_E, top_E))
    EQE_combined    = np.concatenate((bottom_Q, top_Q))
    eqe_extended_spectrum = np.column_stack((Energy_combined, EQE_combined))
    eqe_el = np.column_stack((energy_el, EQE_EL_fitted))
    return eqe_extended_spectrum, eqe_el


def calculate_SQ(Egap: float) -> tuple[float, float]:
    """
    Calculate the Shockley-Queisser limit to the Voc for a given bandgap.

    Parameters:
        > Egap : float          Bandgap [eV]

    Returns:
        > dictionary with the follwing values:
            > Egap : float          Bandgap [eV]
            > Voc_sq : float        Shockley-Queisser limit to the open-circuit voltage [V]
            > Jsc_sq : float        Shockley-Queisser limit to the short-circuit current [V]
    """
    Egap = np.atleast_1d(Egap)
    
    # Energy grid
    energy = np.linspace(0.1, 4.0, 10000)

    # Load solar spectrum
    solar_spectrum = load_solar_spectrum()
    E_sun, phi_sun = solar_spectrum[:, 0], solar_spectrum[:, 1]
    phi_interp = np.interp(energy, E_sun, phi_sun)

    # Black-body photon flux
    phi_BB = black_body_radiation(energy)

    # Preallocate arrays
    Voc_sq = np.zeros_like(Egap)
    Jsc_sq = np.zeros_like(Egap)

    # Integrate for each Egap
    for i, Eg in enumerate(Egap):
        mask = energy > Eg
        Jsc_sq[i] = np.trapezoid(phi_interp[mask], energy[mask])
        J0_sq = q*q * np.trapezoid(phi_BB[mask], energy[mask])
        Voc_sq[i] = kT * np.log(Jsc_sq[i] / J0_sq + 1)

    # If single input, return scalars
    if Voc_sq.size == 1:
        Voc_sq = Voc_sq.item()
        Jsc_sq = Jsc_sq.item()

    return {
        "Bandgap (eV)": Eg,
        "Voc_sq (V)": Voc_sq,
        "Jsc_sq (A/cm²)": Jsc_sq,
    }

def calculate_vocrad(eqe_spectrum_extended: NDArray[np.float64], integration_range) -> float:
    """
    Calculate the radiative-limit open-circuit voltage (Voc_rad) from an extended EQE spectrum.

    Parameters:
        > eqe_spectrum_extended : ndarray of shape (N, 2)           Extended EQE(E) spectrum (energy [eV], EQE [fractional]).
        > integration_range : list[float]                           Energy range [Emin, Emax] (eV) for evaluating the integrals.

    Returns:
    -------
        > float:  Radiative-limit open-circuit voltage Voc_rad (V).
    """
    Emin, Emax = integration_range
    # ensure the spectrum is sorted:
    eqe_spectrum_extended = _sort_spectrum(eqe_spectrum_extended)
    
    energy = eqe_spectrum_extended[:,0]
    eqe = eqe_spectrum_extended[:,1]    

    phi_BB = black_body_radiation(energy)
    solar_spectrum = load_solar_spectrum()
    E_sun, phi_sun = solar_spectrum[:, 0], solar_spectrum[:, 1]

    phi_sun_interp = np.interp(energy, E_sun, phi_sun)

    integ_range = (energy >= Emin) & (energy <= Emax)

    J0_rad  = q*q * np.trapezoid(phi_BB[integ_range]*eqe[integ_range], energy[integ_range])
    Jsc_EQE =       np.trapezoid(phi_sun_interp*eqe, energy)

    Voc_rad = kT * np.log(Jsc_EQE / J0_rad + 1)

    return Voc_rad

def calculate_voltage_losses(eqe_spectrum: NDArray[np.float64], el_spectrum: NDArray[np.float64], voc_device: float, integration_range, fit_range) -> pd.DataFrame:
    """
    Calculate bandgap, and voltage loss components from an EQE, EL spectrum, and the device Voc.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
    Parameters:
        > eqe_spectrum : ndarray of shape (N, 2)    EQE(E) spectrum (energy [eV], EQE [fractional]).
        > el_spectrum : ndarray of shape (M, 2)     Electroluminescence spectrum for reciprocity extension.
        > voc_device : float                        Measured open-circuit voltage of the device (V).

    Returns
    -------
    pandas.DataFrame
        Single-row table with Eg, Voc_sq, Voc_rad, voc_device,
        and voltage losses DV1_sq, DV2_rad, DV3_nrad.
    """
    Eg, eqe_derivative = calculate_bandgap(eqe_spectrum)
    sq_results = calculate_SQ(Egap = Eg)
    Voc_sq = sq_results["Voc_sq (V)"]
    eqe_extended, eqe_el = extend_eqe_reciprocity(eqe_spectrum, el_spectrum, fit_range)
    Voc_rad = calculate_vocrad(eqe_extended, integration_range)

    dv1_sq   = Eg - Voc_sq
    dv2_rad  = Voc_sq - Voc_rad
    dv3_nrad = Voc_rad - voc_device

    spectra = {}
    spectra["eqe_dev"] = eqe_spectrum
    spectra["el"] = el_spectrum
    spectra["eqe_el"] = eqe_el
    spectra["eqe_extended"] = eqe_extended
    spectra["eqe_derivative"] = eqe_derivative

    voltage_loss_results = pd.DataFrame([{
        "Eg (eV)": Eg,
        "Voc_sq (V)": Voc_sq,
        "Voc_rad (V)": Voc_rad,
        "voc_device (V)": voc_device,
        "DV1_sq (eV)": dv1_sq,
        "DV2_rad (eV)": dv2_rad,
        "DV3_nr (eV)": dv3_nrad
    }])

    return voltage_loss_results, spectra
