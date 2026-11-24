# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:34:58 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt

DATA_ROLE = Qt.ItemDataRole.UserRole
CHECKED = Qt.CheckState.Checked

if TYPE_CHECKING:
    from ..data.mfli_leaf_node_info import MFLILeafNodeInfo

    from ..gui.ppms_lockin_measurement_main_window import PPMSLockinMeasurementMainWindow
    from ..gui.daq_server_widget import DAQServerWidget

    from .session import Session
    from .daq_server import DAQServer
    from .data_server import DataServer
    from .configuration import Configuration
    from .save_settings import SaveSettings
    from .header_table_entry import HeaderTableEntry
    from .streaming_table_entry import StreamingTableEntry


def load_session_dataclass(main_window: PPMSLockinMeasurementMainWindow, session: Session) -> None:
    """
    Takes all the information of the given session and applies it to the given main window.

    Parameters
    ----------
    main_window : PPMSLockinMeasurementMainWindow
        The main window, to which the session should be applied.
    session : Session
        The session, which should fill the main window.

    Returns
    -------
    None
    """

    main_window.sequence_filename: str = session.sequence_filename
    main_window.sequence_le.setText(main_window.sequence_filename)
    main_window.log_filename: str = session.log_filename
    main_window.logfile_le.setText(main_window.log_filename)
    main_window.single_measurement_cb.setChecked(session.single_measurement)
    main_window.on_single_measurement(session.single_measurement)
    main_window.save_folder: str = session.save_folder
    main_window.save_folder_le.setText(main_window.save_folder)
    main_window.filename_prefix_le.setText(session.filename_prefix)
    for index, daq_server in enumerate(session.daq_servers):
        load_daq_server_dataclass(main_window, daq_server, index)


def load_daq_server_dataclass(
    main_window: PPMSLockinMeasurementMainWindow, daq_server: DAQServer, index: int
) -> None:
    """
    Takes the information of the given DAQ server and applies it to the given main window in the
    tab with the given index.

    Parameters
    ----------
    main_window : PPMSLockinMeasurementMainWindow
        The main window, to which the DAQ server settings should be applied.
    daq_server : DAQServer
        The DAQ server information, which should fill the tab in the main window.
    index : int
        The index of the tab, which should be configured.

    Returns
    -------
    None
    """

    if index != 0:
        main_window.daq_server_tab_widget.add_tab()
    w: DAQServerWidget = main_window.daq_server_tab_widget.widget(index).layout().itemAt(0).widget()
    main_window.daq_server_tab_widget.setTabText(index, daq_server.tab_name)

    load_data_server_dataclass(daq_server.data_server, w)
    if daq_server.data_server.connected:
        load_configuration_dataclass(daq_server.configuration, w)
        load_save_settings_dataclass(daq_server.save_settings, w)


def load_data_server_dataclass(data_server: DataServer, w: DAQServerWidget) -> None:
    """
    Takes the information of the given data server and applies it to the given DAQ server widget.

    Parameters
    ----------
    data_server : DataServer
        The data server, which should fill the DAQ server widget.
    w : DAQServerWidget
        The DAQ server widget, which should be configured.

    Returns
    -------
    None
    """

    w.host_le.setText(data_server.host)
    w.port_le.setText(data_server.port)
    if data_server.connected:
        w.toggle_connection(None)


def load_configuration_dataclass(configuration: Configuration, w: DAQServerWidget) -> None:
    """
    Takes the information of the given configuration and applies it to the given DAQ server widget.

    Parameters
    ----------
    configuration : Configuration
        The configuration, which should fill the DAQ server widget.
    w : DAQServerWidget
        The DAQ server widget, which should be configured.

    Returns
    -------
    None
    """

    w.temperature_cb.setChecked(configuration.temperature_selected)
    w.field_cb.setChecked(configuration.field_selected)
    w.rotator_pos_cb.setChecked(configuration.rotator_position_selected)
    w.sampling_rate_dsb.setValue(configuration.sampling_rate)

    for leaf_item in w.configure_node_dialog._leaf_items():  # pylint: disable=protected-access
        node: MFLILeafNodeInfo = leaf_item.data(0, DATA_ROLE)
        if node.path in configuration.selected_header_nodes:
            leaf_item.setCheckState(1, CHECKED)
        if node.path in configuration.selected_streaming_nodes:
            leaf_item.setCheckState(0, CHECKED)


def load_save_settings_dataclass(save_settings: SaveSettings, w: DAQServerWidget) -> None:
    """
    Takes the information of the save settings and applies it to the given DAQ server widget.

    Parameters
    ----------
    save_settings : SaveSettings
        The save settings, which should fill the DAQ server widget.
    w : DAQServerWidget
        The DAQ server widget, which should be configured.

    Returns
    -------
    None
    """

    w.filename_suffix_le.setText(save_settings.filename_suffix)
    for index, header_table_entry in enumerate(save_settings.header_table_entries):
        load_header_table_entry_dataclass(header_table_entry, w, index)

    for index, streaming_table_entry in enumerate(save_settings.streaming_table_entries):
        load_streaming_table_entry_dataclass(streaming_table_entry, w, index)


def load_header_table_entry_dataclass(
    header_table_entry: HeaderTableEntry, w: DAQServerWidget, index: int
) -> None:
    """
    Takes the information of the header table entry and applies it to the given header table row
    with the given index in the DAQ server widget.

    Parameters
    ----------
    header_table_entry : HeaderTableEntry
        The header table entry, which should fill the table in the DAQ server widget.
    w : DAQServerWidget
        The DAQ server widget, which should be configured.
    index : int
        The row number of the table in the DAQ server widget.

    Returns
    -------
    None
    """

    used_header_nodes: dict[str, MFLILeafNodeInfo] = {
        node.path: node for node in w.configure_node_dialog.get_only_header_checked_nodes()
    }
    node_path: str = header_table_entry.node_path
    save_name: str = header_table_entry.save_name
    if node_path not in used_header_nodes:
        print(f"Could not connect to node '{node_path}'!")
    else:
        w.header_nodes_table.add_row(used_header_nodes[node_path])
        w.header_nodes_table.cellWidget(index, 0).setText(save_name)
        w.header_nodes_table.nodes.append(used_header_nodes[node_path])


def load_streaming_table_entry_dataclass(
    streaming_table_entry: StreamingTableEntry, w: DAQServerWidget, index: int
) -> None:
    """
    Takes the information of the header table entry and applies it to the given header table row
    with the given index in the DAQ server widget.

    Parameters
    ----------
    streaming_table_entry : StreamingTableEntry
        The streaming table entry, which should fill the table in the DAQ server widget.
    w : DAQServerWidget
        The DAQ server widget, which should be configured.
    index : int
        The row number of the table in the DAQ server widget.

    Returns
    -------
    None
    """

    used_streaming_nodes: dict[str, MFLILeafNodeInfo] = {
        node.path: node for node in w.configure_node_dialog.get_only_checked_nodes()
    }
    node_path: str = streaming_table_entry.node_path
    save_name: str = streaming_table_entry.save_name
    std_dev_selected: bool = streaming_table_entry.std_dev_selected
    len_selected: bool = streaming_table_entry.len_selected
    if node_path not in used_streaming_nodes:
        print(f"Could not connect to node '{node_path}'!")
    else:
        w.streaming_nodes_table.add_row(used_streaming_nodes[node_path])
        w.streaming_nodes_table.cellWidget(index, 0).setText(save_name)
        w.streaming_nodes_table.cellWidget(index, 1).setChecked(std_dev_selected)
        w.streaming_nodes_table.cellWidget(index, 2).setChecked(len_selected)
        w.streaming_nodes_table.nodes.append(used_streaming_nodes[node_path])
