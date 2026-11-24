# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:12:09 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import os

import MultiPyVu as mpv

from .mfli_data_interpreter import MFLIDataInterpreter

if TYPE_CHECKING:
    from .mfli_leaf_node_info import MFLILeafNodeInfo
    from ..threads.ppms_status_values import PPMSStatusValues
    from zhinst.core import ziDAQServer


class MultiVuDataFileHandler:  # pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-positional-arguments
    """
    A class to hold all information of a node from the MFLI to which the DAQ can subscribe to.

    Parameters
    ----------
    filename : str
        The filename with which the new MultiVu .dat file should be saved.
    ppms_status_values : PPMSStatusValues
        The dictionary in which the current values of the PPMS are saved like temperature, field,
        etc.
    daq : ziDAQServer
        The DAQ server, from which the data is saved in this datafile.
    nodes_to_evaluate : list[MFLILeafNodeInfo]
        The list of nodes which should be evaluated from the pulled data of the MFLI.
    nodes_to_evaluate_std : list[MFLILeafNodeInfo] | None
        The list of nodes which standard deviation from the pulled data of the MFLI should be
        computed and saved. The default is None, which results in an empty list.
    nodes_to_evaluate_len : list[MFLILeafNodeInfo] | None
        The list of nodes which length from the pulled data of the MFLI should be computed and
        saved. The default is None, which results in an empty list.
    nodes_in_header : list[MFLILeafNodeInfo] | None
        The list of nodes which should be only saved once in the header of the new .dat file.
        The default is None, which results in an empty list.
    nodes_save_names : dict[MFLILeafNodeInfo, str] | None
        A dictionary, which maps a node to the corresponding name of this column in the new .dat
        file. The default is None, which results in an empty dictionary.
    force_new_file : bool
        A new file will be created, also if it exists already. The default is True.
    save_temperature : bool
        If the temperature should be saved to the new .dat file. The default is True.
    save_field : bool
        If the field should be saved to the new .dat file. The default is True.
    save_rotator : bool
        If the rotator position should be saved to the new .dat file. The default is False.


    Attributes
    ----------
    filename : str
        The filename with which the new MultiVu .dat file should be saved.
    ppms_status_values : PPMSStatusValues
        The dictionary in which the current values of the PPMS are saved like temperature, field,
        etc.
    daq : ziDAQServer
        The DAQ server, from which the data is saved in this datafile.
    nodes_to_evaluate : list[MFLILeafNodeInfo]
        The list of nodes which should be evaluated from the pulled data of the MFLI.
    nodes_to_evaluate_std : list[MFLILeafNodeInfo] | None
        The list of nodes which standard deviation from the pulled data of the MFLI should be
        computed and saved.
    nodes_to_evaluate_len : list[MFLILeafNodeInfo] | None
        The list of nodes which length from the pulled data of the MFLI should be computed and
        saved.
    nodes_in_header : list[MFLILeafNodeInfo] | None
        The list of nodes which should be only saved once in the header of the new .dat file.
    nodes_save_names : dict[MFLILeafNodeInfo, str] | None
        A dictionary, which maps a node to the corresponding name of this column in the new .dat
        file.
    force_new_file : bool
        A new file will be created, also if it exists already.
    save_temperature : bool
        If the temperature should be saved to the new .dat file.
    save_field : bool
        If the field should be saved to the new .dat file.
    save_rotator : bool
        If the rotator position should be saved to the new .dat file.
    datafile : mpv.DataFile
        The python object corresponding to the new MultiVu .dat file.
    mfli_data_interpreter : MFLIDataInterpreter
        The interpreter which will convert the pulled data from the MFLI according to the given
        nodes and computes the standard deviation and/or length of the data, if needed.

    """

    def __init__(
        self,
        filename: str,
        ppms_status_values: PPMSStatusValues,
        daq: ziDAQServer,
        nodes_to_evaluate: list[MFLILeafNodeInfo],
        nodes_to_evaluate_std: list[MFLILeafNodeInfo] | None = None,
        nodes_to_evaluate_len: list[MFLILeafNodeInfo] | None = None,
        nodes_in_header: list[MFLILeafNodeInfo] | None = None,
        nodes_save_names: dict[MFLILeafNodeInfo, str] | None = None,
        force_new_file: bool = True,
        save_temperature: bool = True,
        save_field: bool = True,
        save_rotator: bool = False,
    ) -> None:

        self.filename: str = filename
        self.ppms_status_values: PPMSStatusValues = ppms_status_values
        self.daq: ziDAQServer = daq
        self.nodes_to_evaluate: list[MFLILeafNodeInfo] = nodes_to_evaluate or []
        self.nodes_to_evaluate_std: list[MFLILeafNodeInfo] = nodes_to_evaluate_std or []
        self.nodes_to_evaluate_len: list[MFLILeafNodeInfo] = nodes_to_evaluate_len or []
        self.nodes_in_header: list[MFLILeafNodeInfo] = nodes_in_header or []
        self.nodes_save_names: dict[str, str] = nodes_save_names or {}

        self.force_new_file: bool = force_new_file
        self.save_temperature: bool = save_temperature
        self.save_field: bool = save_field
        self.save_rotator: bool = save_rotator

        self.datafile: mpv.DataFile = mpv.DataFile()
        self.mfli_data_interpreter: MFLIDataInterpreter = MFLIDataInterpreter(
            nodes_to_evaluate, nodes_to_evaluate_std, nodes_to_evaluate_len
        )

        self.column_mapping: dict[str, str] = {}

    def generate_column_headers(self) -> list[str]:
        """
        Generates the list in which all the column headers are written.

        Returns
        -------
        list[str]
            The list containing all column headers for the new .dat file.
        """

        result: str = []
        if self.save_temperature:
            result.append("Temperature [K]")
        if self.save_field:
            result.append("Field [Oe]")
        if self.save_rotator:
            result.append("Rotator position [deg]")
        for node in self.nodes_to_evaluate:
            column_name: str = ""
            if node in self.nodes_save_names.keys():
                column_name: str = self.nodes_save_names[node]
            else:
                column_name: str = node.path_streaming
            result.append(column_name)
            self.column_mapping.update({node.path_streaming: column_name})

            if node in self.nodes_to_evaluate_std:
                if node in self.nodes_save_names.keys():
                    column_name: str = self.nodes_save_names[node] + " [std]"
                else:
                    column_name: str = node.path_streaming + "_std"
                result.append(column_name)
                self.column_mapping.update({node.path_streaming + "_std": column_name})

            if node in self.nodes_to_evaluate_len:
                if node in self.nodes_save_names.keys():
                    column_name: str = self.nodes_save_names[node] + " [len]"
                else:
                    column_name: str = node.path_streaming + "_len"
                result.append(column_name)
                self.column_mapping.update({node.path_streaming + "_len": column_name})
        return result

    def generate_nodes_in_header_info(self) -> str:
        """
        Generates the string which will be saved as the title of the new .dat file. In this title
        there will be the values of the nodes, which only should be printed in the header. Due to
        new line characters, this can be achived by formating the title accordingly.

        Returns
        -------
        str
            The new title for the .dat file.

        Raises
        ------
        ValueError
            If a type from a node is not knwon.
        """

        result: str = ""
        for node in self.nodes_in_header:
            if "Integer" in node.node_type:
                value: int = int(self.daq.getInt(node.path))
            elif "Double" in node.node_type:
                value: float = float(self.daq.getDouble(node.path))
            elif "String" in node.node_type:
                value: str = str(self.daq.getString(node.path))
            else:
                raise ValueError(f"Unknown node type: {node.node_type}")
            name: str = self.nodes_save_names.get(node, node.path)
            result: str = f"{result}\nINFO, {name}, {value}"
        return result

    def generate_filename(self) -> str:
        """
        Generates a non existing filename by appending an increasing number.

        Returns
        -------
        str
            The non existing filename.
        """

        if not os.path.isfile(self.filename):
            return self.filename
        for i in range(10000):
            if not os.path.isfile(
                self.filename.split(".")[0] + f"_{i:04}." + self.filename.split(".")[1]
            ):
                break
        return self.filename.split(".")[0] + f"_{i:04}." + self.filename.split(".")[1]

    def create_file(self) -> None:
        """
        Creates the new .dat file and writes the header to it.

        Returns
        -------
        None
        """

        if self.force_new_file:
            self.filename: str = self.generate_filename()
        self.datafile.add_multiple_columns(self.generate_column_headers())
        self.datafile.create_file_and_write_header(
            self.filename, self.filename[:-4] + self.generate_nodes_in_header_info()
        )

    def configure_daq(self) -> None:
        """
        Configures the DAQ server by subscribing all nodes to it that should be evaluated.

        Returns
        -------
        None
        """

        for path_subscribable in {node.path_subscribable for node in self.nodes_to_evaluate}:
            self.daq.subscribe(path_subscribable)

    def acquire_data(self, avg_time: float, timeout: int = 500) -> None:
        """
        Acquires the data from one poll from the DAQ server, interpretes this data and saves it to
        the new .dat file.

        Parameters
        ----------
        avg_time : float
            The time the DAQ server listens to the data server.
        timeout : int, optional
            The timeout for the poll. The default is 500.

        Returns
        -------
        None
        """

        data: dict = self.daq.poll(avg_time, timeout)
        interpreted_data: dict[str, float | int | str] = (
            self.mfli_data_interpreter.interprete_nested_dict(data)
        )
        for path_streaming, value in interpreted_data.items():
            self.datafile.set_value(self.column_mapping[path_streaming], value)
        ppms_values: dict[str, float] = self.ppms_status_values.snapshot()
        if self.save_temperature:
            self.datafile.set_value("Temperature [K]", ppms_values["temperature"])
        if self.save_field:
            self.datafile.set_value("Field [Oe]", ppms_values["field"])
        if self.save_rotator:
            self.datafile.set_value("Rotator position [deg]", ppms_values["rotator position"])
        self.datafile.write_data()
