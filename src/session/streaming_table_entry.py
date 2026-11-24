# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 12:03:40 2026

@author: Administrator
"""

from dataclasses import dataclass


@dataclass
class StreamingTableEntry:
    """
    A dataclass to store information about an entry in the streaming table of the save settings.

    Attributes
    ----------
    node_path : str
        The path of the node in the entry.
    save_name : str
        The custom name of the node.
    std_dev_selected : bool
        If the standard deviation should also be saved.
    len_selected : bool
        If the length should also be saved.
    """

    node_path: str = ""
    save_name: str = ""
    std_dev_selected: bool = False
    len_selected: bool = False

    @classmethod
    def from_dict(cls, d : dict) -> StreamingTableEntry:
        """
        Creats the class from the information given in the dictionary.

        Parameters
        ----------
        d : dict
            The dictionary which holds all the information for this class.

        Returns
        -------
        StreamingTableEntry
            The constructed class.
        """
        return cls(**d)
