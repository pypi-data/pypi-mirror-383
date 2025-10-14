# PVVoltLoss, Photovoltaic Voltage-Loss Analysis

Author: Jolanda S. Müller, Imperial College London
License: BSD 3-Clause

## Overview

PVVoltLoss is an analysis and visualisation toolkit for determining the bandgap and voltage losses in photovoltaic devices from their external quantum efficiency (EQE) and electroluminescence (EL) spectra. The tool is an interactive graphical interface (GUI) to load, visualise, and analyse spectra.
A headless CLI mode (--nogui) for scripted or automated analysis is also available.

This package follows the Shockley–Queisser and Rau reciprocity frameworks to quantify bandgap [1,2], absorption onset limited, and non-radiative loss components from experimental spectra [3,4]. (See citations at the end of the readme)

## Installation

### Option 1
Direct installation as python package via pip install in Python. This option does not require to download the repository, but also does not allow to modify the tool. In command line run:
```
pip install pvvoltloss
```

### Option 2
Clone the repository and install in editable mode (recommended during development). This option allows to see and modify the source code.

```
git clone https://github.com/Jenny-Nelson-Group/pvvoltloss.git
cd voltagelosses
python -m venv venv
source venv/bin/activate     # (Linux/macOS)
pip install -e .
```

All dependencies (NumPy, Pandas, SciPy, Matplotlib) are handled automatically from requirements.txt.

### Test (For Both Options)
To verify that the package was installed properly run in the command line:
```
pvvoltloss --help
```
This should show a list of all possible parameters that can be specified when running the tool.

## Usage
### Option 1 – Graphical User Interface (default)

In the Python environment where you installed pvvoltloss, run the following command in the command line:
```
pvvoltloss
```

or, equivalently:
```
python -m pvvoltloss
```

This launches a Tk-based GUI where you can:
- Load EQE and EL spectra (.csv or .txt). Different columns can be selected for Energy and EQE/E - default first 2 columns.
- Adjust fitting range (range in which EQE_EL is scaled to best match with EQE_dev)
- Adjust integration range (range for calculating J0rad)
- Visualise the EQE that is extended with the EL via reciprocity
- Inspect extracted bandgap, Voc_sq, Voc_rad, and voltage loss components
- Export results (results/voltage_losses.csv) and spectra tables

Optionally, parameters can be passed directly upon launching the gui:
```
pvvoltloss
  --eqe input/example_EQE.csv \
  --el  input/example_EL.csv \
  --voc 0.916 \
  --fit 1.30:1.40 \
  --irange 0.7:3.0 \
  --device MyDeviceName
```

When exporting the voltage loss results, the device name and calculated parameters are saved to a csv file (default: voltage_losses.csv) in the /results folder. On consecutive saves to the same filename the user has the option to append the results or overwrite. By appending results from different devices it will create csv file where each column shows the voltage losses of a differnt device.

Spectra are exported in a csv table, which can be convieniently imported into e.g. Origin for plotting.

More information can be obtained via
```
pvvoltloss --help
```


### Option 2 – Command-line (headless) Mode

To run without user interface, add the --noigui keyword. Needs at least --eqe, --el, and --voc as further keywrods. (Or --example)

Exmple:
```
pvvoltloss
  --nogui
  --eqe input/example_EQE.csv \
  --el  input/example_EL.csv \
  --eqe_cols 0:2\
  --voc 0.916 \
  --fit 1.30:1.40 \
  --irange 0.7:3.0 \
  --device MyCell
```

The tool prints results to stdout and writes both result and spectra CSV files in a ./results folder relative to where the tool is executed.

### Command Line Parameters (Compatible with GUI or nogui)
```
  -h, --help           show this help message and exit
  --nogui              Run headless CLI workflow. Requires --eqe, --el, --voc; OR --example.
  --example            Run with example data. Can be used in headless or GUI mode. Individual parameters can be overridden (e.g. --voc 0.9).
  --eqe EQE            Path to EQE data file (CSV or TXT). First column: energy (eV), second column: EQE. Preloads EQE in GUI mode
  --el EL              Path to EL data file (CSV or TXT). First column: energy (eV), second column: EL (arb. units). Preloads EL in GUI mode
  --voc VOC            Open-circuit voltage of the device (V)
  --eqe_cols EQE_COLS  Define which columns in the EQE file correspond to Energy and EQE; default: first two columns 0:1
  --el_cols EL_COLS    Define which columns in the EL file correspond to Energy and EL; default: first two columns 0:1
  --fit FIT            Fitting range (eV) specifies in which range EQE_EL is matched to EQE_dev, default 1.30:1.40
  --irange IRANGE      Integration range (eV) specifies in which range J0rad and Jsc are integrated, default 0.8:3.0
  --out OUT            Output CSV file for voltage losses. Default path: results/voltage_losses.csv
  --device DEVICE      Device name, will be added as the first column in the output CSV and in filename of spectra. Default: 'sample'
```

### Example Output
```
Eg (eV) Voc_sq (V)	Voc_rad (V)	voc_device (V)	ΔV₁_sq (eV)	ΔV₂_rad (eV)	ΔV₃_nr (eV)
1.45    1.32	1.19	0.92	0.30	0.13	0.227
```

## Core Modules
- physics.py          Implements reciprocity and Shockley–Queisser loss analysis, including bandgap determination and radiative/non-radiative voltage components.
- data_handler.py	    File I/O utilities for importing spectra and exporting results (with overwrite/append dialog).
- gui.py   Tkinter-based GUI for interactive analysis and plotting.
- nogui.py	          Headless analysis function for CLI use.
- cli.py	            Command-line parser and entry point.
- run.py	            Convenience script allowing users to run without installing the package. However, package installation is preferred.

## Citation
If you use this tool for academic work, please cite:

Müller, Jolanda. S. (2025). PVVoltLoss – Photovoltaic Voltage-Loss Analysis Tools [Python package]. Imperial College London. Available at: https://github.com/Jenny-Nelson-Group/pvvoltloss.git


### Relevant Theory
Regarding Bandgap Calculations:
- U. Rau, B. Blank, T. C. Müller, and T. Kirchartz. “Efficiency Potential of Photovoltaic Materials and Devices Unveiled by Detailed-Balance Analysis”. Physical Review Applied 7.4 (2017). DOI: 10.1103/PhysRevApplied.7.044016.
- Y. Wang, D. Qian, Y. Cui, H. Zhang, J. Hou, K. Vandewal, T. Kirchartz, and F. Gao. “Optical Gaps of Organic Solar Cells as a Reference for Comparing Voltage Losses”. Advanced Energy Materials 8.28 (2018). DOI: 10.1002/aenm. 201801352.

Regarding Non-Radiative Voltage Loss Analysis:
- U. Rau. “Reciprocity relation between photovoltaic quantum efficiency and electroluminescent emission of solar cells”. Physical Review B - Condensed Matter and Materials Physics 76.8 (2007). DOI: 10.1103/PhysRevB.76.085303.
- J. Yao, T. Kirchartz, M. S. Vezie, M. A. Faist, W. Gong, Z. He, H. Wu, J. Troughton, T. Watson, D. Bryant, and J. Nelson. “Quantifying losses in opencircuit voltage in solution-processable solar cells”. Physical Review Applied 4.1 (2015), pp. 1–10. DOI: 10.1103/PhysRevApplied.4.014020.


## License
This project is licensed under the BSD 3-Clause License, © 2025 Imperial College London.


## Acknowledgements
Developed within the Nelson Group at the Department of Physics, Imperial College London.
Based on foundational work by U. Rau, J. Yao, Y. Wang, T. Kirchartz, and collaborators on reciprocity and voltage loss analysis in organic photovoltaics.
