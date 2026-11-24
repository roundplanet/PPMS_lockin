# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:48:31 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt

from .session import Session
from .daq_server import DAQServer
from .data_server import DataServer
from .configuration import Configuration
from .save_settings import SaveSettings
from .header_table_entry import HeaderTableEntry
from .streaming_table_entry import StreamingTableEntry

if TYPE_CHECKING:
    from ..data.mfli_leaf_node_info import MFLILeafNodeInfo

    from ..gui.ppms_lockin_measurement_main_window import PPMSLockinMeasurementMainWindow
    from ..gui.daq_server_widget import DAQServerWidget

DATA_ROLE = Qt.ItemDataRole.UserRole
CHECKED = Qt.CheckState.Checked


def create_session_dataclass(main_window: PPMSLockinMeasurementMainWindow) -> Session:
    """
    Creates a Session object, which holds all the needed information from the main window to reload
    the session.

    Parameters
    ----------
    main_window : PPMSLockinMeasurementMainWindow
        The main window, from which the session should be created.

    Returns
    -------
    Session
        The created session.
    """

    session: Session = Session()
    session.sequence_filename: str = main_window.sequence_le.text()
    session.log_filename: str = main_window.logfile_le.text()
    session.single_measurement: bool = main_window.single_measurement_cb.isChecked()
    session.save_folder: str = main_window.save_folder
    session.filename_prefix: str = main_window.filename_prefix_le.text()
    for index in range(main_window.daq_server_tab_widget.count()):
        session.daq_servers.append(create_daq_server_dataclass(main_window, index))
    return session


def create_daq_server_dataclass(
    main_window: PPMSLockinMeasurementMainWindow, index: int
) -> DAQServer:
    """
    Creates a DAQServer object, which holds all needed information from the DAQ server.

    Parameters
    ----------
    main_window : PPMSLockinMeasurementMainWindow
        The main window, from which the DAQ server should be created.
    index : int
        The index of the tab in which the DAQ server is.

    Returns
    -------
    DAQServer
        The created DAQ server.
    """

    w: DAQServerWidget = main_window.daq_server_tab_widget.widget(index).layout().itemAt(0).widget()

    daq_server: DAQServer = DAQServer()
    daq_server.tab_name: str = main_window.daq_server_tab_widget.tabText(index)
    daq_server.data_server: DataServer = create_data_server_dataclass(w)
    daq_server.configuration: Configuration = create_configuration_dataclass(w)
    if w.configure_node_dialog is not None:
        daq_server.save_settings: SaveSettings = create_save_settings_dataclass(w)
    return daq_server


def create_data_server_dataclass(w: DAQServerWidget) -> DataServer:
    """
    Creates a DataServer object, which holds all needed information from the data server.

    Parameters
    ----------
    w : DAQServerWidget
        The DAQ server widget, from which the data server will be created.

    Returns
    -------
    DataServer
        The created data server.
    """

    data_server: DataServer = DataServer()
    data_server.host: str = w.host_le.text()
    data_server.port: str = w.port_le.text()
    data_server.connected: bool = w.disconnect_pb.isEnabled()
    return data_server


def create_configuration_dataclass(w: DAQServerWidget) -> Configuration:
    """
    Creates a Configuration object, which holds all needed information from the configuration box.

    Parameters
    ----------
    w : DAQServerWidget
        The DAQ server widget, from which the configuration will be created.

    Returns
    -------
    Configuration
        The created configuration.
    """

    configuration: Configuration = Configuration()
    configuration.temperature_selected: bool = w.temperature_cb.isChecked()
    configuration.field_selected: bool = w.field_cb.isChecked()
    configuration.rotator_position_selected: bool = w.rotator_pos_cb.isChecked()
    configuration.sampling_rate: float = w.sampling_rate_dsb.value()
    if w.configure_node_dialog is not None:
        configuration.selected_header_nodes: list[str] = [
            node.path for node in w.configure_node_dialog.get_only_header_checked_nodes()
        ]
        configuration.selected_streaming_nodes: list[str] = [
            node.path for node in w.configure_node_dialog.get_only_checked_nodes()
        ]
    return configuration


def create_save_settings_dataclass(w: DAQServerWidget) -> SaveSettings:
    """
    Creates a SaveSettings object, which holds all needed information from the save settings box.

    Parameters
    ----------
    w : DAQServerWidget
        The DAQ server widget, from which the save settings will be created.

    Returns
    -------
    SaveSettings
        The created save settings.
    """

    save_settings: SaveSettings = SaveSettings()
    save_settings.filename_suffix: str = w.filename_suffix_le.text()

    for node, custom_name in w.header_nodes_table.generate_save_dict().items():
        save_settings.header_table_entries.append(
            create_header_table_entry_dataclass(node, custom_name)
        )

    std_list: list[MFLILeafNodeInfo] = w.streaming_nodes_table.generate_std_list()
    len_list: list[MFLILeafNodeInfo] = w.streaming_nodes_table.generate_len_list()
    for node, custom_name in w.streaming_nodes_table.generate_save_dict().items():
        save_settings.streaming_table_entries.append(
            create_streaming_table_entry_dataclass(
                node, custom_name, node in std_list, node in len_list
            )
        )
    return save_settings


def create_header_table_entry_dataclass(
    node: MFLILeafNodeInfo, custom_name: str
) -> HeaderTableEntry:
    """
    Creates a HeaderTableEntry object, which holds all needed information from a header table entry.

    Parameters
    ----------
    node : MFLILeafNodeInfo
        The node which is displayed in the header table.
    custom_name : str
        The costum name of the node.

    Returns
    -------
    HeaderTableEntry
        The created header table entry.
    """

    header_table_entry: HeaderTableEntry = HeaderTableEntry()
    header_table_entry.node_path: str = node.path
    header_table_entry.save_name: str = custom_name
    return header_table_entry


def create_streaming_table_entry_dataclass(
    node: MFLILeafNodeInfo, custom_name: str, std_dev_selected: bool, len_selected: bool
) -> StreamingTableEntry:
    """
    Creates a StreamingTableEntry object, which holds all needed information from a streaming table
    entry.

    Parameters
    ----------
    node : MFLILeafNodeInfo
        The node which is displayed in the streaming table.
    custom_name : str
        The costum name of the node.

    Returns
    -------
    StreamingTableEntry
        The created streaming table entry.
    """

    streaming_table_entry: StreamingTableEntry = StreamingTableEntry()
    streaming_table_entry.node_path: str = node.path
    streaming_table_entry.save_name: str = custom_name
    streaming_table_entry.std_dev_selected: bool = std_dev_selected
    streaming_table_entry.len_selected: bool = len_selected
    return streaming_table_entry
