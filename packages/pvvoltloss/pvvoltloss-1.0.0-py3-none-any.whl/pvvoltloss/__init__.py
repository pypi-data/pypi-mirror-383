# src/pvvoltloss/__init__.py
#####################################################################################
# OPV Voltage Loss Package
#
# API: Entry point when running from within a python script,
# or called by cli.py when package is run from command line.
# Author: Jolanda S Müller, Imperial College London
# Copyright (c) 2025, Imperial College London, BSD 3-Clause License
# Date: October 2025
#####################################################################################

from .config import Config, layer_configs
from . import physics
from . import data_handler
from dataclasses import asdict

__all__ = ["run", "physics", "data_handler"]
__version__ = "1.0.0"

def run(*, mode: str = "gui", example=False, **kwargs):
    """Runs the program in gui mode or nogui mode, with an option to use example values."""
    user_config = Config(**kwargs)

    config = layer_configs(
        Config.get_defaults(),
        Config.get_example() if example else None,
        user_config
        )

    # check that nogui mode has all necessary inputs
    if mode == "nogui" and not example:
        if (config.eqe == None) or (config.el == None):
            print(f"--nogui requires --eqe and --el data (or use --example)")
            return

    # execute either GUI or noGUI mode
    if mode == "nogui":
        from .nogui import run_headless
        return run_headless(config)
    elif mode == "gui":
        from .gui import launch_gui
        return launch_gui(config)

    raise ValueError("mode must be 'gui' or 'nogui'")