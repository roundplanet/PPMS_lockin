# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 15:25:55 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView, QCheckBox
from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from ..data.mfli_leaf_node_info import MFLILeafNodeInfo


class StreamingNodesTable(QTableWidget):
    """
    A subclass of QTableWidget, which shows all given node elements in a table. There the user can
    give the node a custom name for the .dat file in which the data is saved and if the standard
    deviation and/or the length should be saved as well.

    Parameters
    ----------
    nodes : list[MFLILeafNodeInfo] | None
        A list of all nodes, that should be displayed in the table. The default is None, which
        results in an empty list.

    Attributes
    ----------
    nodes : list[MFLILeafNodeInfo]
        A list of nodes, which are displayed in the table.


    """

    def __init__(self, nodes: list[MFLILeafNodeInfo] | None = None) -> None:
        super().__init__(0, 3)
        self.setHorizontalHeaderLabels(["custom name", "save std. dev.", "save len"])
        vh: QHeaderView = self.verticalHeader()
        vh.setSectionsMovable(True)
        vh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        vh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        hh: QHeaderView = self.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in (1, 2):
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        self.nodes: list[MFLILeafNodeInfo] = nodes or []
        for node in self.nodes:
            self.add_row(node)

    def add_row(self, node: MFLILeafNodeInfo) -> None:
        """
        Adds a row to the table with the contents of the specified node.

        Parameters
        ----------
        node : MFLILeafNodeInfo
            The node which should fill the new row.

        Returns
        -------
        None
        """

        row: int = self.rowCount()

        self.blockSignals(True)
        self.insertRow(row)
        header: QTableWidgetItem = QTableWidgetItem(node.path)
        header.setData(Qt.ItemDataRole.UserRole, node)
        self.setVerticalHeaderItem(row, header)

        self.setCellWidget(row, 0, QLineEdit())
        self.cellWidget(row, 0).setText(node.path)
        if "Stream" in node.properties:
            self.setCellWidget(row, 1, QCheckBox())
            self.setCellWidget(row, 2, QCheckBox())

    def generate_save_dict(self) -> dict[MFLILeafNodeInfo, str]:
        """
        Generates the dictionary from the contents of the table, which maps the nodes to their
        custom names.

        Returns
        -------
        dict[MFLILeafNodeInfo, str]
            The dicitonary, which maps the node to its costum name.
        """

        result: dict[MFLILeafNodeInfo:str] = {}
        vh: QHeaderView = self.verticalHeader()
        for visual in range(self.rowCount()):
            row: int = vh.logicalIndex(visual)
            node: MFLILeafNodeInfo = self.verticalHeaderItem(row).data(Qt.ItemDataRole.UserRole)
            custom_name: str = self.cellWidget(row, 0).text()
            result.update({node: custom_name})
        return result

    def generate_std_list(self) -> list[MFLILeafNodeInfo]:
        """
        Generates a list of nodes, which standard deviation should also be saved in the measurement.

        Returns
        -------
        list[MFLILeafNodeInfo]
            The list of nodes, where the standard deviation should be saved.
        """

        result: list[MFLILeafNodeInfo] = []
        vh: QHeaderView = self.verticalHeader()
        for visual in range(self.rowCount()):
            row: int = vh.logicalIndex(visual)
            if isinstance(self.cellWidget(row, 1), QCheckBox):
                if self.cellWidget(row, 1).isChecked():
                    node: MFLILeafNodeInfo = self.verticalHeaderItem(row).data(
                        Qt.ItemDataRole.UserRole
                    )
                    result.append(node)
        return result

    def generate_len_list(self) -> list[MFLILeafNodeInfo]:
        """
        Generates a list of nodes, which length should also be saved in the measurement.

        Returns
        -------
        list[MFLILeafNodeInfo]
            The list of nodes, where the length should be saved.
        """

        result: list[MFLILeafNodeInfo] = []
        vh: QHeaderView = self.verticalHeader()
        for visual in range(self.rowCount()):
            row: int = vh.logicalIndex(visual)
            if isinstance(self.cellWidget(row, 2), QCheckBox):
                if self.cellWidget(row, 2).isChecked():
                    node: MFLILeafNodeInfo = self.verticalHeaderItem(row).data(
                        Qt.ItemDataRole.UserRole
                    )
                    result.append(node)
        return result

    def repopulate(self, new_nodes: list[MFLILeafNodeInfo]):
        """
        Removes all current nodes, which are not in the new list and adds the missing ones to the
        table.

        Parameters
        ----------
        new_nodes : list[MFLILeafNodeInfo]
            The list of the new nodes, which should be displayed in the table.

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
