# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 12:31:08 2026

@author: Administrator
"""

from dataclasses import dataclass


@dataclass
class DataServer:
    """
    A dataclass to store information about the data server of a DAQ server.

    Attributes
    ----------
    host : str
        The host of the data server.
    port : int
        The port of the data server.
    connected : bool
        If the DAQ server was connected to the data server.
    """

    host: str = "localhost"
    port: int = 8004
    connected: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> DataServer:
        """
        Creats the class from the information given in the dictionary.

        Parameters
        ----------
        d : dict
            The dictionary which holds all the information for this class.

        Returns
        -------
        DataServer
            The constructed class.
        """

        return cls(**d)
