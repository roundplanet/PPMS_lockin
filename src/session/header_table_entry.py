# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 12:26:51 2026

@author: Administrator
"""

from dataclasses import dataclass


@dataclass
class HeaderTableEntry:
    """
    A dataclass to store information about an entry in the header table of the save settings.

    Attributes
    ----------
    node_path : str
        The path of the node in the entry.
    save_name : str
        The custom name of the node.
    """

    node_path: str = ""
    save_name: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> HeaderTableEntry:
        """
        Creats the class from the information given in the dictionary.

        Parameters
        ----------
        d : dict
            The dictionary which holds all the information for this class.

        Returns
        -------
        HeaderTableEntry
            The constructed class.
        """

        return cls(**d)
