"""
NAME 
    simulation.py

DESCRIPTION
    This module contains the Simulation dataclass, 
    which is used to store the data of a simulation.

CLASSES
    Simulation
"""
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class Simulation:
    """
        A dataclass for storing the data of one numerical simulation of EM fields.

        Attributes
        ----------
        name : str
            The name of the simulation.
        path : Path
            The path to the simulation data.
        e_field : np.array, optional
            The electric field data.
        h_field : np.array, optional
            The magnetic field data.    
        object_masks : np.array, optional
            The object masks.
        features : np.array, optional
            The physical features - permittivity, permeability, conductivity.
        resulting_path : Path, optional
            The path to the resulting `.h5` file
    """

    name: str
    path: Path
    e_field: Optional[np.array] = None
    h_field: Optional[np.array] = None
    object_masks: Optional[np.array] = None
    features: Optional[np.array] = None
    resulting_path: Optional[Path] = None
