# src/pvvoltloss/data_handler.py
#####################################################################################
# OPV Voltage Loss Package
#
# data_handler module: Holds all functions responsible for data input/output
# Author: Jolanda S Müller, Imperial College London
# Copyright (c) 2025, Imperial College London, BSD 3-Clause License
# Date: October 2025
#####################################################################################

import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.simpledialog as sd
import pandas as pd
import csv
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from importlib.resources import files

class TwoIntBox(sd.Dialog):
    """Small dialog to input two integers (e.g. column indices)."""
    def __init__(self, parent, label_text="Value 1; Value 2", default=(0, 1), **kwargs):
        self.label_text = label_text
        self.default = default
        super().__init__(parent, **kwargs)
    def body(self, master):
        tk.Label(master, text=self.label_text).grid(row=0,column=0,columnspan=2,pady=(4,6))
        self.x=tk.IntVar(value=self.default[0]); self.y=tk.IntVar(value=self.default[1])
        tk.Entry(master,textvariable=self.x,width=4).grid(row=1,column=0)
        tk.Entry(master,textvariable=self.y,width=4).grid(row=1,column=1)
    def apply(self): self.result=(self.x.get(),self.y.get())


def import_example_data() -> np.ndarray:
    eqe_path = files("pvvoltloss.data.examples") / "example_EQE.csv"
    el_path = files("pvvoltloss.data.examples") / "example_EL.csv"
    eqe, _ = import_data(file_path=eqe_path)
    el, _  = import_data(file_path=el_path)

    return eqe, el

def import_data( file_path = None, message="Select file", columns=(0,1))  -> tuple[np.ndarray, str]:
    """
    Import data from a file (e.g. EQE spectrum). Default column 0 and 1.

    Parameters:
        > file_path : str | None        (Path to the data file. If None, open a file dialog.)
        > message : str                 (Message displayed in file dialog title.)
        > col_x, col_y : int | None     (Column indices to import (0-based). Default: first two columns.)

    Returns:
        > data : np.ndarray             (Array of shape (N, 2) containing the selected columns.)
        > filename : str                (Name of the imported file (without path).)
    """
    # Automatically run in GUI MODE if no file path is given
    if file_path == None:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title=message, initialdir="./input")
        if not file_path:
            return np.empty((0, 2)), ""
        
        columns = TwoIntBox(None,title="Column Indices...", label_text="Energy Column  ;  Data Column").result
    
    # Load data from file. compatible with: .csv, .txt, .xls, .xlsx 
    ext = os.path.splitext(file_path)[1].lower()
    try:
        # excel files
        if ext in (".xls", ".xlsx"):
            df = pd.read_excel(file_path, header=1)
            loaded_data = df.to_numpy()
        # csv or txt
        else:
            delimiter = _sniff_delimiter(file_path)
            loaded_data = np.loadtxt(file_path, delimiter=delimiter)
    except Exception as e:
        messagebox.showerror("Import error", f"Could not read file:\n{e}")
        return np.empty((0, 2)), ""

    # check that the file has at least two columns
    if loaded_data.shape[1] < 2:
        messagebox.showerror("Import error", "File must have at least two numeric columns.")
        return np.empty((0, 2)), ""
    
    #Check specified columns exists
    col_x, col_y = map(int, columns)
    if col_x >= loaded_data.shape[1] or col_y >= loaded_data.shape[1]:
        messagebox.showerror("Import error", f"File has only {loaded_data.shape[1]} columns. Cannot select columns {col_x} and {col_y}.")
        return np.empty((0, 2)), ""
    
    #select columns specified in "columns" tupel
    loaded_data = loaded_data[:, [col_x, col_y]]

    filename = os.path.basename(file_path)
    return loaded_data, filename

def _sniff_delimiter(file_path: str):
    """Detect delimiter; fallback to None (=whitespace)."""
    with open(file_path, "r", newline="") as f:
        sample = f.read(4096)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t ")
            return dialect.delimiter
        except csv.Error:
            return None

def export_voltage_losses(device_name: str, df: pd.DataFrame, choice=None, gui_mode=True) -> None:
    """
    Open a save dialog and export a voltage-loss table (DataFrame) to CSV.
    The device name will be added as the first column.
    If the file exists, ask the user to overwrite, append, or cancel.
    """
    root = tk.Tk()
    root.withdraw()
    try:
        if gui_mode == False:
            path = "results/voltage_losses.csv"
        else:
            path = filedialog.asksaveasfilename(
                title="Save voltage-loss table",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                confirmoverwrite=False,
                initialdir="results",
                initialfile="voltage_losses.csv"
            )
            if not path:
                return

        df_export = df.copy()
        df_export.insert(0, "Device", device_name)  # Add device name as first column

        if os.path.exists(path):
            # Custom dialog for Overwrite/Append/Cancel
            if choice is None:
                win = tk.Toplevel(root)
                win.title("File exists")
                tk.Label(win, text="File already exists.\nWhat do you want to do?").pack(padx=20, pady=10)
                result = {"choice": None}
                def set_choice(choice):
                    result["choice"] = choice
                    win.destroy()
                tk.Button(win, text="Overwrite", width=10, command=lambda: set_choice("overwrite")).pack(side=tk.LEFT, padx=10, pady=10)
                tk.Button(win, text="Append", width=10, command=lambda: set_choice("append")).pack(side=tk.LEFT, padx=10, pady=10)
                tk.Button(win, text="Cancel", width=10, command=lambda: set_choice("cancel")).pack(side=tk.LEFT, padx=10, pady=10)
                win.grab_set()
                root.wait_window(win)
                choice = result["choice"]

            if choice == "overwrite":
                df_export.to_csv(path, index=False)
            elif choice == "append":
                try:
                    existing = pd.read_csv(path)
                    combined = pd.concat([existing, df_export], ignore_index=True)
                    combined.to_csv(path, index=False)
                except Exception as e:
                    messagebox.showerror("Append failed", f"Could not append to file:\n{e}")
                    return
            else:  # Cancel or closed window
                return
        else:
            df_export.to_csv(path, index=False)
        #messagebox.showinfo("Export complete", f"Saved:\n{path}")
    finally:
        root.destroy()


def export_spectra_columns(filename: str, spectra: dict, gui_mode=True) -> None:
    """
    Export all spectra in the given dictionary to a CSV file.
    Each entry in spectra should be an (N, 2) array.
    The CSV will have columns: energy_<key>, <key> for each entry.
    """
    import numpy as np
    import pandas as pd
    import tkinter as tk
    from tkinter import filedialog

    if gui_mode == False:
        filename = f"results/{filename}_spectra.csv"
    else:
        root = tk.Tk()
        root.withdraw()
        filename = filedialog.asksaveasfilename(
            title="Save spectra as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=filename + "_spectra.csv",
            initialdir="results"
        )
        root.destroy()
        if not filename:
            return  # User cancelled
    
    # Prepare columns
    columns = {}
    max_len = 0
    for key, arr in spectra.items():
        if arr is not None and hasattr(arr, "shape") and arr.shape[0] > 0:
            arr = np.asarray(arr)
            if arr.ndim == 1:
                arr = arr.reshape(-1, 2)
            columns[f"energy_{key}"] = arr[:, 0]
            columns[key] = arr[:, 1]
            max_len = max(max_len, arr.shape[0])

    # Pad columns to max_len
    for k in columns:
        col = columns[k]
        if len(col) < max_len:
            columns[k] = np.pad(col, (0, max_len - len(col)), constant_values=np.nan)

    df = pd.DataFrame(columns)
    df.to_csv(filename, index=False)

def export_figure(fig, name="figure", dimensions=None, gui_mode=True) -> None:
        """Save the currently displayed figure as a PDF."""
        if gui_mode == False:
            file_path = f"results/{name}_plot.pdf"
        else:
            file_path = fd.asksaveasfilename(
            title="Save plot as PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"{name}_plot.pdf",
            initialdir="results"
        )
        if not file_path:
            return  # user cancelled

        if dimensions is not None:
            size_x, size_y = dimensions
        elif dimensions is None and gui_mode == True:
            size_x, size_y = TwoIntBox(None,title="Figure Dimensions (cm)", label_text="width  ;  height", default=(14,12)).result
        else:
            size_x, size_y = 14, 11
      
        try:
            cm = 1 / 2.54
            size = fig.get_size_inches()
            fig.set_size_inches(size_x * cm, size_y * cm)
            fig.figure.savefig(file_path, bbox_inches="tight", transparent=False)
            fig.set_size_inches(size)  # reset to original size
            print(f"- Plot saved to {file_path}")
        except Exception as e:
            mb.showerror("Error", f"Failed to export plot:\n{e}")