# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 12:32:19 2026

@author: Administrator
"""

from dataclasses import dataclass, field

from .data_server import DataServer
from .configuration import Configuration
from .save_settings import SaveSettings


@dataclass
class DAQServer:
    """
    A dataclass to store information about the configuration of a DAQ server.

    Attributes
    ----------
    tab_name : str
        The name of the tab from the DAQ server.
    data_server : DataServer
        The information about the data server.
    configuration : Configuration
        The information about the configuration.
    save_settings : SaveSettings
        The information about the save settigns.
    """

    tab_name: str = ""
    data_server: DataServer = field(default_factory=DataServer)
    configuration: Configuration = field(default_factory=Configuration)
    save_settings: SaveSettings = field(default_factory=SaveSettings)

    @classmethod
    def from_dict(cls, d: dict) -> DAQServer:
        """
        Creats the class from the information given in the dictionary.

        Parameters
        ----------
        d : dict
            The dictionary which holds all the information for this class.

        Returns
        -------
        DAQServer
            The constructed class.
        """

        return cls(
            tab_name=d["tab_name"],
            data_server=DataServer.from_dict(d.get("data_server", {})),
            configuration=Configuration.from_dict(d.get("configuration", {})),
            save_settings=SaveSettings.from_dict(d.get("save_settings", {})),
        )
