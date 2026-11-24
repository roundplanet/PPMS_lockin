# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 15:42:50 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView
from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from ..data.mfli_leaf_node_info import MFLILeafNodeInfo


class HeaderNodesTable(QTableWidget):
    """
    A subclass of QTableWidget, which holds all nodes that value should be saved before the
    measurement in the header. It also enables the user to give each node a custom name, which will
    be displayed in the .dat file instead of the path of the node.

    Parameters
    ----------
    nodes : list[MFLILeafNodeInfo] | None
        The nodes which this table should hold.

    Attributes
    ----------
    nodes : list[MFLILeafNodeInfo] | None
        The nodes which this table hold.

    """

    def __init__(self, nodes: list[MFLILeafNodeInfo] | None = None) -> None:
        super().__init__(0, 1)
        self.setHorizontalHeaderLabels(["custom name"])
        vh = self.verticalHeader()
        vh.setSectionsMovable(True)
        vh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        vh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        hh = self.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.nodes: list[MFLILeafNodeInfo] = nodes or []
        for node in self.nodes:
            self.add_row(node)

    def add_row(self, node: MFLILeafNodeInfo) -> None:
        """
        Adds a row to the table with a QLineEdit, in which the user can give the node a new name.

        Parameters
        ----------
        node : MFLILeafNodeInfo
            The node which should be added to the table.

        Returns
        -------
        None
        """

        row: int = self.rowCount()

        self.blockSignals(True)
        self.insertRow(row)
        header = QTableWidgetItem(node.path)
        header.setData(Qt.ItemDataRole.UserRole, node)
        self.setVerticalHeaderItem(row, header)

        self.setCellWidget(row, 0, QLineEdit())
        self.cellWidget(row, 0).setText(node.path)

    def generate_save_dict(self) -> dict[MFLILeafNodeInfo, str]:
        """
        Generates a dictionary, where each displayed node is mapped to the custom name the user gave
        the node.

        Returns
        -------
        dict[MFLILeafNodeInfo, str]
            The dictionary that maps the node to its designated custom name.
        """

        result: dict[MFLILeafNodeInfo:str] = {}
        vh: QHeaderView = self.verticalHeader()
        for visual in range(self.rowCount()):
            row: int = vh.logicalIndex(visual)
            node: MFLILeafNodeInfo = self.verticalHeaderItem(row).data(Qt.ItemDataRole.UserRole)
            custom_name: str = self.cellWidget(row, 0).text()
            result.update({node: custom_name})
        return result

    def repopulate(self, new_nodes: list[MFLILeafNodeInfo]) -> None:
        """
        Repopulates the table with the new list of nodes. Nodes that are present in the new and old
        list will be kept, old ones removed and the missing ones from the new list added.

        Parameters
        ----------
        new_nodes : list[MFLILeafNodeInfo]
            List of all new nodes that should be displayed in the table.

        Returns
        -------
        None
        """

        for row in reversed(range(self.rowCount())):
            node: MFLILeafNodeInfo = self.verticalHeaderItem(row).data(Qt.ItemDataRole.UserRole)
            if node.path not in [new_node.path for new_node in new_nodes]:
                self.removeRow(row)

        for node in new_nodes:
            if node.path not in [comp_node.path for comp_node in self.nodes]:
                self.add_row(node)

        self.nodes: list[MFLILeafNodeInfo] = new_nodes
