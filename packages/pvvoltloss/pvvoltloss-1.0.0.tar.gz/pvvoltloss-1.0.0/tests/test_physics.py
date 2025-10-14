# tests/test_physics.py
import importlib
import numpy as np
import pandas as pd
import pytest


def test_import_physics():
    import pvvoltloss.physics as physics
    assert hasattr(physics, "__doc__")

def test_load_solar_spectrum():
    import pvvoltloss.physics as physics
    spec = physics.load_solar_spectrum()
    # Accept either pandas or numpy output; just check it's non-empty
    if isinstance(spec, pd.DataFrame):
        assert not spec.empty
        assert spec.shape[1] >= 2
    else:
        arr = np.asarray(spec)
        assert arr.ndim == 2 and arr.shape[1] >= 2

def test_calculate_SQ_skalar_input():
    import pvvoltloss.physics as physics
    # test value calculation for skalar input
    sq = physics.calculate_SQ(Egap=1.4) # in eV
    
    # check that sq is a dictionary with expected keys
    assert isinstance(sq, dict)
    assert "Voc_sq (V)" in sq
    assert "Jsc_sq (A/cm²)" in sq

    # test value calculation for skalar input
    Voc_sq = sq["Voc_sq (V)"]
    Jsc_sq = sq["Jsc_sq (A/cm²)"]
    # check that Voc_sq value is equal to 1.136, with some wiggle room for numerical differences
    assert np.isclose(Voc_sq, 1.1365792303608406, atol=1e-4)
    assert np.isclose(Jsc_sq, 32.85599228683904, atol=1e-4)

def test_calculate_SQ_multiple_inputs():
    import pvvoltloss.physics as physics
    # test value calculation for multiple inputs
    Eg_values = [1.1, 1.34, 1.5, 2.0]  # in eV
    
    sq = physics.calculate_SQ(Egap=Eg_values)
    assert isinstance(sq, dict)
    assert "Voc_sq (V)" in sq
    assert "Jsc_sq (A/cm²)" in sq
    Voc_sq_values = sq["Voc_sq (V)"]
    Jsc_sq_values = sq["Jsc_sq (A/cm²)"]
    assert len(Voc_sq_values) == len(Eg_values)
    assert len(Jsc_sq_values) == len(Eg_values)
    # Check that values are within expected ranges
    for Voc_sq, Jsc_sq in zip(Voc_sq_values, Jsc_sq_values):
        assert np.isfinite(Voc_sq) and Voc_sq > 0
        assert np.isfinite(Jsc_sq) and Jsc_sq > 0


def test_calculate_bandgap():
    # testing bandgap value on example data
    import pvvoltloss.physics as physics
    from pvvoltloss.data_handler import import_example_data
    eqe, _ = import_example_data()
    Eg, derivative = physics.calculate_bandgap(eqe)
    assert np.isclose(Eg, 1.452298225002984, atol=1e-4), f"Calculated bandgap {Eg} deviates from expected 1.45 eV"

def test_calculate_bandgap_derivative():
    # testing dimensionality of derivate based on interpolation values
    import pvvoltloss.physics as physics
    from pvvoltloss.data_handler import import_example_data
    eqe, _ = import_example_data()
    _, derivative_int1 = physics.calculate_bandgap(eqe, interp_factor=1)
    _, derivative_int5 = physics.calculate_bandgap(eqe, interp_factor=5)
    assert derivative_int1.shape == eqe.shape
    assert derivative_int5.shape[0] == 5 * eqe.shape[0]

def test_example_data():
    from importlib.resources import files
    from pvvoltloss.data_handler import import_example_data
    from pvvoltloss.physics import calculate_voltage_losses
    from pvvoltloss.config import Config

    example_config = Config.get_example()

    eqe, el = import_example_data()
    voc = example_config.voc
    integration_range = example_config.int_range
    fit_range = example_config.fit_range
    
    voltage_loss_results, spectra = calculate_voltage_losses(
        eqe_spectrum=eqe,
        el_spectrum=el,
        voc_device=voc,
        integration_range=integration_range,
        fit_range=fit_range
        )
    
    # check return data type
    assert isinstance(spectra, dict)
    assert isinstance(voltage_loss_results, pd.DataFrame)

    # check the values match the expected values:
    #Eg (eV)  Voc_sq (V)  Voc_rad (V)  voc_device (V)  DV1_sq (eV)  DV2_rad (eV)  DV3_nr (eV)
    #1.452298    1.185238     1.144872           0.916     0.267061      0.040365     0.228872
    expected = {
        "Eg (eV)": 1.452298,
        "Voc_sq (V)": 1.185238,
        "Voc_rad (V)": 1.144872,
        "voc_device (V)": 0.916,
        "DV1_sq (eV)": 0.267061,
        "DV2_rad (eV)": 0.040365,
        "DV3_nr (eV)": 0.228872
    }
    for key, val in expected.items():
        assert key in voltage_loss_results.columns
        assert np.isclose(voltage_loss_results[key].values[0], val, atol=1e-4), f"Value for {key} differs: expected {val}, got {voltage_loss_results[key].values[0]}"