# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 12:33:56 2026

@author: Administrator
"""

from dataclasses import dataclass, field

from .daq_server import DAQServer


@dataclass
class Session:
    """
    A dataclass to store information about a complete session.

    Attributes
    ----------
    sequence_filename : str
        The filename of the sequence file.
    log_filename : str
        The filename of the logfile.
    single_measurement : bool
        If the measurement is a single measurement, thus a monitoring of the sequence is not
        neccessary.
    save_folder : str
        The folder to which the data should be saved.
    filename_prefix : str
        The prefix of the final filename.
    daq_servers : list[DAQServer]
        The list of DAQ servers, which will retriev data from the data server during the
        measurement.
    """

    sequence_filename: str = ""
    log_filename: str = ""
    single_measurement: bool = False
    save_folder: str = ""
    filename_prefix: str = ""
    daq_servers: list[DAQServer] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> Session:
        """
        Creats the class from the information given in the dictionary.

        Parameters
        ----------
        d : dict
            The dictionary which holds all the information for this class.

        Returns
        -------
        Session
            The constructed class.
        """

        return cls(
            sequence_filename=d.get("sequence_filename", ""),
            log_filename=d.get("log_filename", ""),
            single_measurement=d.get("single_measurement", False),
            save_folder=d.get("save_folder", ""),
            filename_prefix=d.get("filename_prefix", ""),
            daq_servers=[DAQServer.from_dict(c) for c in d.get("daq_servers", [])],
        )
