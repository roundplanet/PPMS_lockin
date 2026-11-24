# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 17:36:53 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import os

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QTreeWidgetItem, QTreeWidgetItemIterator
from PyQt6.QtCore import Qt, pyqtSignal, QEvent

from .header_box_delegate import HeaderBoxDelegate

if TYPE_CHECKING:
    from zhinst.core import ziDAQServer
    from ..data.mfli_leaf_node_info_container import MFLILeafNodeInfoContainer
    from ..data.mfli_leaf_node_info import MFLILeafNodeInfo

DATA_ROLE = Qt.ItemDataRole.UserRole
CHECKED = Qt.CheckState.Checked
UNCHECKED = Qt.CheckState.Unchecked
CHECKABLE = Qt.ItemFlag.ItemIsUserCheckable
TRISTATE = Qt.ItemFlag.ItemIsAutoTristate


class SelectNodesToLogDialog(QDialog):
    """
    A subclass of QDialog to show the defined constants in the constant file.

    Parameters
    ----------
    node_container : MFLILeafNodeInfoContainer
        The container filled with all nodes from the DAQ server.
    daq : ziDAQServer
        The DAQ server, which nodes are displayed in this dialog.

    Attributes
    ----------
    old : dict[str, (int, int)]
        Keeps track of all connected nodes and maps their path to the last selected states of their
        corresponding checkboxes.
    daq : ziDAQServer
        The DAQ server, which nodes are displayed in this dialog.
    node_container : MFLILeafNodeInfoContainer
        The container filled with all nodes from the DAQ server.
    tree_items : dict[str, QTreeWidgetItem]
        A dictionary which maps the path of a node to its corresponding represenative in the tree
        widget.

    """

    hidden: pyqtSignal = pyqtSignal()

    def __init__(self, node_container: MFLILeafNodeInfoContainer, daq: ziDAQServer) -> None:
        super().__init__()
        uic.loadUi(
            "/".join(os.path.abspath(__file__).split("\\")[:-1])
            + "/ui-files/select_nodes_to_log.ui",
            self,
        )
        self.setModal(True)

        self.tree.setColumnWidth(0, 320)
        self.tree.setColumnWidth(1, 110)
        self.tree.setItemDelegateForColumn(1, HeaderBoxDelegate(self.tree))
        self.tree.itemChanged.connect(self._on_item_changed)

        self.ok_pb.clicked.connect(self.hide)
        self.refresh_pb.clicked.connect(self.populate)

        self.old: dict[str, (int, int)] = {}
        self.daq: ziDAQServer = daq
        self.node_container: MFLILeafNodeInfoContainer = node_container
        self.tree_items: dict[str, QTreeWidgetItem] = {}
        self.populate()

    def populate(self) -> None:
        """
        Emtpies the QTreeWidget, repopulates it with the entries from the
        data server who can be read and reapplies the former ticked boxes if
        applicable. Attaches to each QTreeWidgetItem the node itself.

        Returns
        -------
        None.
        """
        for item in self._leaf_items():
            self.old.update(
                {
                    item.data(0, DATA_ROLE).path[1:]: (
                        item.checkState(0),
                        item.checkState(1),
                    )
                }
            )

        self.tree.clear()
        self.tree_items.clear()
        self.node_container.fill(self.daq)

        for node in self.node_container:
            if "Read" in node.properties:
                parent: QTreeWidgetItem = self.tree.invisibleRootItem()
                key: str = ""
                for index, part in enumerate(node.path[1:].split("/")):
                    key: str = f"{key}/{part}" if key else part
                    if key not in self.tree_items:
                        if index == len(node.path[1:].split("/")) - 1:
                            item: QTreeWidgetItem = QTreeWidgetItem(
                                parent, [part, "", node.node_type, node.unit, node.description]
                            )
                            item.setFlags(item.flags() | CHECKABLE)
                            item.setCheckState(
                                0, self.old.get(key)[0] if key in self.old else UNCHECKED
                            )
                            item.setCheckState(
                                1, self.old.get(key)[1] if key in self.old else UNCHECKED
                            )
                            item.setData(0, DATA_ROLE, node)
                        else:
                            item: QTreeWidgetItem = QTreeWidgetItem(parent, [part])
                            item.setFlags(item.flags() | CHECKABLE | TRISTATE)
                            item.setCheckState(0, Qt.CheckState.Unchecked)
                        self.tree_items[key]: QTreeWidgetItem = item

                    parent: QTreeWidgetItem = self.tree_items[key]

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Handles the change in a checkbox state. If a 'Node' checkbox is unticked,
        but the 'Only in header' checkbox is still ticked, then it will be
        unticked.

        Parameters
        ----------
        item : QTreeWidgetItem
            The item which changed.
        column : int
            The column in which the change occured.

        Returns
        -------
        None
        """

        if column not in (0, 1) or item.childCount() > 0:
            return
        if column == 0 and item.checkState(0) == UNCHECKED and item.checkState(1) != UNCHECKED:
            item.setCheckState(1, UNCHECKED)
        elif column == 1 and item.checkState(0) == UNCHECKED and item.checkState(1) != UNCHECKED:
            item.setCheckState(0, CHECKED)
        self.tree.viewport().update()

    def _leaf_items(self) -> QTreeWidgetItem:
        """
        A generator to loop over all leaf nodes.

        Yields
        ------
        QTreeWidgetItem
            A QTreeWidgetItem from the QTreeWidget.
        """

        it: QTreeWidgetItemIterator = QTreeWidgetItemIterator(self.tree)
        while item := it.value():
            if item.data(0, DATA_ROLE) is not None:
                yield item
            it += 1

    def get_checked_nodes(self) -> list[MFLILeafNodeInfo]:
        """
        Gets all checked nodes. The state of the 'Only in header' checkbox
        won't influence the result.

        Returns
        -------
        list[MFLILeafNodeInfo]
            The collected nodes.
        """

        result: list[MFLILeafNodeInfo] = []
        for item in self._leaf_items():
            if item.checkState(0) == CHECKED:
                result.append(item.data(0, DATA_ROLE))
        return result

    def get_only_checked_nodes(self) -> list[MFLILeafNodeInfo]:
        """
        Gets all checked nodes, where the checkbox in 'Only in header' is not
        ticked.

        Returns
        -------
        list[MFLILeafNodeInfo]
            The collected nodes.
        """

        result: list[MFLILeafNodeInfo] = []
        for item in self._leaf_items():
            if item.checkState(0) == CHECKED and item.checkState(1) == UNCHECKED:
                result.append(item.data(0, DATA_ROLE))
        return result

    def get_only_header_checked_nodes(self) -> list[MFLILeafNodeInfo]:
        """
        Gets all checked nodes, where the checkbox in 'Only in header' is ticked.

        Returns
        -------
        list[MFLILeafNodeInfo]
            The collected nodes.
        """
        result: list[MFLILeafNodeInfo] = []
        for item in self._leaf_items():
            if item.checkState(0) == CHECKED and item.checkState(1) == CHECKED:
                result.append(item.data(0, DATA_ROLE))
        return result

    def hideEvent(self, event: QEvent) -> None:  # pylint: disable=invalid-name
        """
        Adds to the parent hideEvent the emittion of the own hidden signal, which indicates, that
        the dialog is hidden.

        Parameters
        ----------
        event : QEvent
            The emitted event.

        Returns
        -------
        None
        """

        super().hideEvent(event)
        self.hidden.emit()

    def closeEvent(self, event: QEvent) -> None:  # pylint: disable=invalid-name
        """
        If the dialog should be closed, the closing will be avoided and the dialog hidden instead.

        Parameters
        ----------
        event : QEvent
            The emitted event from closing the dialog.

        Returns
        -------
        None
        """

        event.ignore()
        self.hide()
