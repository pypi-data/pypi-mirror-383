# tests/test_data_handler.py
import importlib
import numpy as np
import pandas as pd
import pytest

def test_import_physics():
    import pvvoltloss.data_handler as data_handler
    assert hasattr(data_handler, "__doc__")

def test_import_example_data():
    from importlib.resources import files
    from pvvoltloss.data_handler import import_data
    eqe_path = files("pvvoltloss.data.examples") / "example_EQE.csv"
    el_path  = files("pvvoltloss.data.examples") / "example_EL.csv"
    eqe, eqe_name = import_data(file_path=eqe_path)
    el, el_name   = import_data(file_path=el_path)
    assert eqe is not None and hasattr(eqe, "shape") and eqe.shape[1] == 2
    assert el is not None and hasattr(el, "shape") and el.shape[1] == 2

def test_import_example_direct():
    from pvvoltloss.data_handler import import_example_data
    eqe, el = import_example_data()
    assert eqe is not None and hasattr(eqe, "shape") and eqe.shape[1] == 2
    assert el is not None and hasattr(el, "shape") and el.shape[1] == 2

