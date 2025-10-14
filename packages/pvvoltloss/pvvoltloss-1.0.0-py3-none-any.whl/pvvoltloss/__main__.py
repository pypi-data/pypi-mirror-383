# src/pvvoltloss/__main__.py
#####################################################################################
# OPV Voltage Loss Package
#
# Package main, called when executing "python3 pvvoltloss.py",
# forwards call directly to console line input interpreter in cli.py
# Author: Jolanda S Müller, Imperial College London
# Copyright (c) 2025, Imperial College London, BSD 3-Clause License
# Date: October 2025
#####################################################################################

from .cli import main
if __name__ == "__main__":
    main()