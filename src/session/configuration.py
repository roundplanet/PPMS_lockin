# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 12:28:48 2026

@author: Administrator
"""

from dataclasses import dataclass, field


@dataclass
class Configuration:
    """
    A dataclass to store information about the configuration of a DAQ server.

    Attributes
    ----------
    temperature_selected : bool
        If the temperature should also be saved.
    field_selected : bool
        If the field should also be saved.
    rotator_position_selected : bool
        If the rotator position should also be saved.
    sampling_rate : float
        The time between to data calls.
    selected_header_nodes : list[str]
        The paths of the nodes, which data should be saved in the header in the beginning of the
        measurement.
    selected_streaming_nodes : list[str]
        The paths of the nodes, which data should be continously saved.
    """

    temperature_selected: bool = True
    field_selected: bool = True
    rotator_position_selected: bool = False
    sampling_rate: float = 0.4
    selected_header_nodes: list[str] = field(default_factory=list)
    selected_streaming_nodes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, bool | float | list[str]]) -> Configuration:
        """
        Creats the class from the information given in the dictionary.

        Parameters
        ----------
        d : dict[str, bool | float | list[str]]
            The dictionary which holds all the information for this class.

        Returns
        -------
        Configuration
            The constructed class.
        """

        return cls(
            temperature_selected=d["temperature_selected"],
            field_selected=d["field_selected"],
            rotator_position_selected=d["rotator_position_selected"],
            sampling_rate=d["sampling_rate"],
            selected_header_nodes=list(d.get("selected_header_nodes", [])),
            selected_streaming_nodes=list(d.get("selected_streaming_nodes", [])),
        )
