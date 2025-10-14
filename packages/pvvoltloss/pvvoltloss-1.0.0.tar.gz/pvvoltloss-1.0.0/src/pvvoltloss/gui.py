# src/pvvoltloss/gui.py
#####################################################################################
# OPV Voltage Loss Package
#
# GUI Module: Creates userinterface for voltage loss analysis
# Author: Jolanda S Müller, Imperial College London
# Copyright (c) 2025, Imperial College London, BSD 3-Clause License
# Date: October 2025
#####################################################################################

import sys
import tkinter as tk
from tkinter import ttk, StringVar, DoubleVar

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .data_handler import import_data, export_voltage_losses, export_spectra_columns, export_figure
from . import physics as physics
from .plotting import update_plot
from . import Config

def launch_gui(config: Config):
    """Launches the gui application with prespecified configurations."""
    app = VoltageLossApplication(
        voc=config.voc,
        eqe_path=config.eqe,
        el_path=config.el,
        device_name=config.device,
        fit_range=config.fit_range,
        int_range=config.int_range,
    )
    app.mainloop()

class VoltageLossApplication(tk.Tk):
    def __init__(
            self,
            voc,
            device_name,
            fit_range,
            int_range,
            eqe_path=None,
            el_path=None,
            ):
        super().__init__()
        self.title("EQE-EL Voltage-Loss Analyser")
        self.geometry("1000x650")

        # Data
        self.eqe_spectrum = None
        self.el_spectrum = None
        self.eqe_el = None
        self.eqe_derivative = None
        self.results = None

        # Data loader
        self.eqe_filename = StringVar(value="No EQE loaded")
        self.el_filename = StringVar(value="No EL loaded")

        # Parameters
        self.fit_low    = DoubleVar(value=fit_range[0])
        self.fit_high   = DoubleVar(value=fit_range[1])
        self.int_low    = DoubleVar(value=int_range[0])
        self.int_high   = DoubleVar(value=int_range[1])
        self.voc_device = DoubleVar(value=voc)

        # Results display
        self.device_name = StringVar(value=device_name)
        self.res_Egap   = StringVar(value="-")
        self.res_Vocsq  = StringVar(value="-")
        self.res_Vocrad = StringVar(value="-")
        self.res_dv1    = StringVar(value="-")
        self.res_dv2    = StringVar(value="-")
        self.res_dv3    = StringVar(value="-")

        # style for green button
        style = ttk.Style(self)
        style.configure("TButton", width=12)
        style.configure("Default.TButton", width=12)
        style.configure("Green.TButton", background="#4CAF50", foreground="white")
        style.map("Green.TButton",
                  background=[('active', '#45a049'), ('!active', '#4CAF50')])

        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()
        self._start(voc=voc, eqe_path=eqe_path, el_path=el_path, device=device_name)

    def _start(self, voc=None, eqe_path=None, el_path=None, device=None):
        # Load EQE if path provided
        if eqe_path is not None:
            eqe, filename = import_data(file_path=eqe_path)
            if eqe is not None and hasattr(eqe, "size") and eqe.size > 0:
                self.eqe_spectrum = eqe
                self.eqe_filename.set(filename if filename else str(eqe_path))
                self.btn_load_eqe.config(style="Green.TButton")

        # Load EL if path provided
        if el_path is not None:
            el, filename = import_data(file_path=el_path)
            if el is not None and hasattr(el, "size") and el.size > 0:
                self.el_spectrum = el
                self.el_filename.set(filename if filename else str(el_path))
                self.btn_load_el.config(style="Green.TButton")
        
        self.update()

    def _on_close(self):
        plt.close("all")
        self.quit()
        self.destroy()
        sys.exit(0)

    def _build_ui(self):
        # Plot frame
        plot_frame = ttk.Frame(self)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        fig, ax = plt.subplots(figsize=(6,5))
        self.ax = ax
        self.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        ax.set_xlabel("Energy (eV)")
        ax.set_ylabel("EQE (fraction)")
        ax.set_yscale("log")

        # Control frame
        ctrl = ttk.Frame(self)
        ctrl.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=4)

        button_width = 20  # pixels
        
        eqe_frame = ttk.Frame(ctrl)
        eqe_frame.pack(fill=tk.X)
        self.btn_load_eqe = ttk.Button(eqe_frame, text="Load EQE", command=self.load_eqe)
        self.btn_load_eqe.pack(side=tk.LEFT, ipadx=button_width//2)  # Internal padding to force width
        ttk.Label(eqe_frame, textvariable=self.eqe_filename, foreground="#555").pack(side=tk.LEFT, padx=4)

        el_frame = ttk.Frame(ctrl)
        el_frame.pack(fill=tk.X, pady=(0,8))
        self.btn_load_el = ttk.Button(el_frame, text="Load EL", command=self.load_el)
        self.btn_load_el.pack(side=tk.LEFT, ipadx=button_width//2)  # Internal padding to force width
        ttk.Label(el_frame, textvariable=self.el_filename, foreground="#555").pack(side=tk.LEFT, padx=4)

        def labeled_spin(text, var, from_, to_, step=0.01):
            fr = ttk.Frame(ctrl); fr.pack(fill=tk.X, pady=2)
            ttk.Label(fr, text=text, width=14).pack(side=tk.LEFT)
            sp = ttk.Spinbox(fr, textvariable=var, from_=from_, to=to_, increment=step, width=8, command=self.update)
            sp.pack(side=tk.LEFT)

        # Device name input
        ttk.Label(ctrl, text="Device Name", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
        ttk.Entry(ctrl, textvariable=self.device_name).pack(fill=tk.X, pady=(0,4))

        ttk.Separator(ctrl).pack(fill=tk.X, pady=4)
        ttk.Label(ctrl, text="Device Open Circuit Voltage", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
        labeled_spin("voc_device [V]",self.voc_device,0,  2)
        ttk.Separator(ctrl).pack(fill=tk.X, pady=4)

        ttk.Label(ctrl, text="Fit Limits", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
        labeled_spin("Fit low [eV]",  self.fit_low,  0.5, 3)
        labeled_spin("Fit high [eV]", self.fit_high, 0.5, 3)
        ttk.Separator(ctrl).pack(fill=tk.X, pady=4)
        
        ttk.Label(ctrl, text="Integration Range", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
        labeled_spin("Int low [eV]",  self.int_low,  0.5, 4)
        labeled_spin("Int high [eV]", self.int_high, 0.5, 4)
        ttk.Separator(ctrl).pack(fill=tk.X, pady=4)
        
        ttk.Separator(ctrl).pack(fill=tk.X, pady=4)
        ttk.Label(ctrl, text="Results", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
        ttk.Label(ctrl, textvariable=self.res_Egap).pack(anchor=tk.W)
        ttk.Label(ctrl, textvariable=self.res_Vocsq).pack(anchor=tk.W)
        ttk.Label(ctrl, textvariable=self.res_Vocrad).pack(anchor=tk.W)
        ttk.Label(ctrl, textvariable=self.res_dv1).pack(anchor=tk.W)
        ttk.Label(ctrl, textvariable=self.res_dv2).pack(anchor=tk.W)
        ttk.Label(ctrl, textvariable=self.res_dv3).pack(anchor=tk.W)

        ttk.Button(ctrl, text="Export Results", command=self.export).pack(fill=tk.X, pady=6)
        ttk.Button(ctrl, text="Export Spectra", command=self.export_spectra).pack(fill=tk.X, pady=2)
        ttk.Button(ctrl, text="Export Plot (PDF)", command=self.export_plot).pack(fill=tk.X, pady=2)
        
        # auto update on variable change
        for var in (self.fit_low, self.fit_high, self.int_low, self.int_high, self.res_Egap, self.voc_device):
            var.trace_add("write", lambda *args: self.update())

    def load_eqe(self):
        eqe, filename = import_data(file_path=None, message="Select EQE file")
        if eqe is not None and hasattr(eqe, "size") and eqe.size > 0:
            self.eqe_spectrum = eqe
            self.btn_load_eqe.config(style="Green.TButton")
        
            if filename is not None:
                self.eqe_filename.set(filename)
            else:
                self.eqe_filename.set("Error")
        else:
            self.eqe_spectrum = None
            self.btn_load_eqe.config(style="Default.TButton")
            self.eqe_filename.set("No EQE loaded")
        self.update()

    def load_el(self):
        el, filename = import_data(file_path=None, message="Select EL file")
        if el is not None and hasattr(el, "size") and el.size > 0:
            self.el_spectrum = el
            self.btn_load_el.config(style="Green.TButton")
            
            if filename is not None:
                self.el_filename.set(filename)
            else:
                self.el_filename.set("Error")
        else:
            self.el_spectrum = None
            self.btn_load_el.config(style="Default.TButton")
            self.el_filename.set("No EL loaded")
        self.update()

    def update(self):
        if self.eqe_spectrum is None or self.el_spectrum is None or self.eqe_spectrum.size == 0 or self.el_spectrum.size == 0:
            return

        # Extend EQE using reciprocity
        fit_range = (self.fit_low.get(), self.fit_high.get())
        int_range = (self.int_low.get(), self.int_high.get())
        voc_device = self.voc_device.get()

        # Calculate Voc_rad and losses
        df_losses, spectra = physics.calculate_voltage_losses(self.eqe_spectrum, self.el_spectrum, voc_device=voc_device, integration_range=int_range, fit_range=fit_range)
        self.results = df_losses
        self.spectra = spectra
        self.eqe_el = spectra.get("eqe_el")
        self.eqe_derivative = spectra.get("eqe_derivative")
        self.eqe_extended = spectra.get("eqe_extended")

        # Update results
        row = self.results.iloc[0]
        self.res_Egap.set(f"Egap = {row['Eg (eV)']:.3f} eV")
        self.res_Vocsq.set(f"DVoc_sq = {row['Voc_sq (V)']:.3f} eV")
        self.res_Vocrad.set(f"DVoc_rad = {row['Voc_rad (V)']:.3f} eV")
        self.res_dv1.set(f"DV1_sq = {row['DV1_sq (eV)']:.3f} eV")
        self.res_dv2.set(f"DV2_rad = {row['DV2_rad (eV)']:.3f} eV")
        self.res_dv3.set(f"DV3_nrad = {row['DV3_nr (eV)']:.3f} eV")

        # Update plot
        update_plot(
            self.ax,
            eqe_spectrum=self.eqe_spectrum,
            el_spectrum=self.el_spectrum,
            eqe_el=self.eqe_el,
            eqe_derivative=self.eqe_derivative,
            results=self.results,
            fit_low=self.fit_low.get(),
            fit_high=self.fit_high.get(),
            int_low=self.int_low.get(),
            int_high=self.int_high.get(),
            device_name=self.device_name.get()
        )

        self.canvas.draw_idle()

    def export(self):
        if self.results is not None:
            export_voltage_losses(device_name=self.device_name.get(), df=self.results)

    def export_spectra(self):
        export_spectra_columns(filename=self.device_name.get(), spectra=self.spectra)

    def export_plot(self):
        """Save the currently displayed figure as a PDF."""
        export_figure(fig=self.canvas.figure, name=self.device_name.get())
        