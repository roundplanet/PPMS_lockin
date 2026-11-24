# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 16:38:26 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import os

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from zhinst.core import ziDAQServer, errors

from ..data.mfli_leaf_node_info_container import MFLILeafNodeInfoContainer
from .select_nodes_to_log_dialog import SelectNodesToLogDialog
from .header_nodes_table import HeaderNodesTable
from .streaming_nodes_table import StreamingNodesTable

if TYPE_CHECKING:
    from PyQt6.QtCore import QEvent
    from ..data.mfli_leaf_node_info import MFLILeafNodeInfo


class DAQServerWidget(QWidget):  # pylint: disable=too-many-instance-attributes
    """
    A subclass of QWidget in which a DAQ server can be configured.

    Attributes
    ----------
    node_container : MFLILeafNodeInfoContainer
        The spinbox which shows the value of the coil radius.
    daq : ziDAQServer | None
        The DAQ server which settings should be configured.
    connected : bool
        If the connection to the DAQ server is active.
    filename_prefix : str
        The prefix of the final filename.
    filename_suffix : str
        The suffix of the final filename.
    save_folder : str
        The folder in which the resulting new .dat file will be saved.
    header_nodes_table : HeaderNodesTable
        The table in which all nodes are displayed, which value should be saved in the header at the
        beginning of the measurement.
    streaming_nodes_table : StreamingNodesTable
        The table in which all nodes are displayed, which values will be continously saved during
        the measurement.
    """

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(
            "/".join(os.path.abspath(__file__).split("\\")[:-1])
            + "/ui-files/data_server_widget.ui",
            self,
        )

        self.node_container: MFLILeafNodeInfoContainer = MFLILeafNodeInfoContainer()
        self.daq: ziDAQServer | None = None
        self.connected: bool = False
        self.connect_pb.clicked.connect(self.toggle_connection)
        self.disconnect_pb.clicked.connect(self.toggle_connection)

        self.configure_node_dialog: SelectNodesToLogDialog | None = None
        self.configure_nodes_pb.clicked.connect(self.show_configure_nodes_dialog)

        self.filename_prefix: str = ""
        self.filename_suffix: str = ""
        self.save_folder: str = ""
        self.filename_suffix_le.textChanged.connect(self.update_filename_suffix)
        self.update_filename_le()

        self.header_nodes_table: HeaderNodesTable = HeaderNodesTable()
        group_box_layout: QVBoxLayout = QVBoxLayout()
        group_box_layout.addWidget(self.header_nodes_table)
        self.only_in_header_gb.setLayout(group_box_layout)

        self.streaming_nodes_table: StreamingNodesTable = StreamingNodesTable()
        group_box_layout: QVBoxLayout = QVBoxLayout()
        group_box_layout.addWidget(self.streaming_nodes_table)
        self.streaming_gb.setLayout(group_box_layout)

    def toggle_connection(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        Connects or disconnects from the DAQ server, depending on the current state. Adjust the
        enabled state of the corresponding other widgets. If the connection is esatblished, a dialog
        to configure the nodes which should be evaluated will be created, shown and immedeatly
        hidden again.

        Parameters
        ----------
        event : QEvent
            The event from the QPushButton.

        Returns
        -------
        None
        """

        if not self.connected:
            host: str = self.host_le.text()
            port: str = self.port_le.text()
            try:
                self.daq: ziDAQServer = ziDAQServer(host, int(port), 6)
                self.node_container.fill(self.daq)
                self.configure_node_dialog: SelectNodesToLogDialog = SelectNodesToLogDialog(
                    self.node_container, self.daq
                )
                self.configure_node_dialog.hidden.connect(self.on_hide_configure_node_dialog)
                self.configure_node_dialog.show()
                self.configure_node_dialog.hide()
            except ValueError:
                print(f"port '{port}' can't be converted to integer")
                return
            except errors.CoreError as err:
                print(err)
                return

        self.connected: bool = not self.connected
        self.configuration_gb.setEnabled(self.connected)
        self.save_settings_gb.setEnabled(self.connected)
        self.disconnect_pb.setEnabled(self.connected)
        self.connect_pb.setEnabled(not self.connected)
        self.host_le.setEnabled(not self.connected)
        self.port_le.setEnabled(not self.connected)

    def show_configure_nodes_dialog(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        Shows the dialog, in which the nodes can be configured for evaluation.

        Parameters
        ----------
        event : QEvent
            The event from the QPushButton.

        Returns
        -------
        None
        """

        if self.configure_node_dialog is None:
            self.configure_node_dialog: SelectNodesToLogDialog = SelectNodesToLogDialog(
                self.node_container, self.daq
            )
        self.configure_node_dialog.show()

    def on_hide_configure_node_dialog(self) -> None:
        """
        Hides the dialog.

        Returns
        -------
        None
        """

        self.header_nodes_table.repopulate(
            self.configure_node_dialog.get_only_header_checked_nodes()
        )
        self.streaming_nodes_table.repopulate(self.configure_node_dialog.get_only_checked_nodes())

    def update_filename_le(self) -> None:
        """
        Updates the displayed final filename if either the saving folder, prefix or suffix has
        changed.

        Returns
        -------
        None
        """

        if self.save_folder == "":
            if self.filename_suffix == "":
                self.filename_le.setText(f"{self.filename_prefix}.dat")
            else:
                self.filename_le.setText(f"{self.filename_prefix}_{self.filename_suffix}.dat")
        elif self.filename_suffix == "":
            self.filename_le.setText(f"{self.save_folder}/{self.filename_prefix}.dat")
        else:
            self.filename_le.setText(
                f"{self.save_folder}/{self.filename_prefix}_{self.filename_suffix}.dat"
            )

    def update_filename_suffix(self, text: str) -> None:
        """
        Updates the suffix filename and afterwards the final filename.

        Parameters
        ----------
        text : str
            The new suffix.

        Returns
        -------
        None
        """

        self.filename_suffix: str = text
        self.update_filename_le()

    def update_filename_prefix(self, text: str) -> None:
        """
        Updates the prefix filename and afterwards the final filename.

        Parameters
        ----------
        text : str
            The new prefix.

        Returns
        -------
        None
        """

        self.filename_prefix: str = text
        self.update_filename_le()

    def update_save_folder(self, text: str) -> None:
        """
        Updates the save folder and afterwards the final filename.

        Parameters
        ----------
        text : str
            The new save folder.

        Returns
        -------
        None
        """

        self.save_folder: str = text
        self.update_filename_le()

    def generate_save_dict(self) -> dict[MFLILeafNodeInfo, str]:
        """
        Generates the dictionary, where the custom name of each node is connected to the node
        itself.

        Returns
        -------
        dict[MFLILeafNodeInfo, str]
            The mapping between the node and it's custom name.
        """

        header_save_dict: dict[MFLILeafNodeInfo, str] = self.header_nodes_table.generate_save_dict()
        streaming_save_dict: dict[MFLILeafNodeInfo, str] = (
            self.streaming_nodes_table.generate_save_dict()
        )
        return header_save_dict | streaming_save_dict

    def generate_std_list(self) -> list[MFLILeafNodeInfo]:
        """
        Generates the list of the nodes, which standard deviation should also be saved.

        Returns
        -------
        list[MFLILeafNodeInfo]
            The list of the nodes, which standard deviation should also be saved.
        """

        return self.streaming_nodes_table.generate_std_list()

    def generate_len_list(self) -> list[MFLILeafNodeInfo]:
        """
        Generates the list of the nodes, which length should also be saved.

        Returns
        -------
        list[MFLILeafNodeInfo]
            The list of the nodes, which length should also be saved.
        """

        return self.streaming_nodes_table.generate_len_list()
