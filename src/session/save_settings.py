# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 12:27:15 2026

@author: Administrator
"""

from dataclasses import dataclass, field

from .header_table_entry import HeaderTableEntry
from .streaming_table_entry import StreamingTableEntry


@dataclass
class SaveSettings:
    """
    A dataclass to store information about the save settings.

    Attributes
    ----------
    filename_suffix : str
        The suffix of the filename to which the data is saved.
    header_table_entries : list[HeaderTableEntry]
        The list containig all entries in the header table.
    streaming_table_entries : list[StreamingTableEntry]
        The list containig all entries in the streaming table.
    """

    filename_suffix: str = ""
    header_table_entries: list[HeaderTableEntry] = field(default_factory=list)
    streaming_table_entries: list[StreamingTableEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> SaveSettings:
        """
        Creats the class from the information given in the dictionary.

        Parameters
        ----------
        d : dict
            The dictionary which holds all the information for this class.

        Returns
        -------
        SaveSettings
            The constructed class.
        """

        return cls(
            filename_suffix=d["filename_suffix"],
            header_table_entries=[
                HeaderTableEntry.from_dict(c) for c in d.get("header_table_entries", [])
            ],
            streaming_table_entries=[
                StreamingTableEntry.from_dict(c) for c in d.get("streaming_table_entries", [])
            ],
        )
