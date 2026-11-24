# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 15:02:28 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem

if TYPE_CHECKING:
    from PyQt6.QtCore import QModelIndex, QEvent, QAbstractItemModel

CHECKED = Qt.CheckState.Checked


class HeaderBoxDelegate(QStyledItemDelegate):
    """
    A helper class to grey out the 'Only in header' checkbox and blocks clicks on it
    as long as the 'Node' checkbox of the same row is unticked.

    Attributes
    ----------
    parent : QObject
        Constructs an item delegate with the given parent.
    """

    @staticmethod
    def _is_leaf(index: QModelIndex) -> bool:
        """
        Checks if the index of the tree is a leaf node or not.

        Parameters
        ----------
        index : QModelIndex
            The row index of the tree.

        Returns
        -------
        bool
            If the node is a leaf node.
        """

        return not index.model().hasChildren(index)

    def initStyleOption(  # pylint: disable=invalid-name
        self, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        """
        Adds to the parent function that only non-composite leaf nodes have a checkbox in the
        'Only in header' column.

        Parameters
        ----------
        option : QStyleOptionViewItem
            Parameters used to draw an item in a view widget.
        index : QModelIndex
            The row index of the tree.

        Returns
        -------
        None
        """

        super().initStyleOption(option, index)
        if not self._is_leaf(index):
            option.features &= ~QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator
        elif "Element of" in index.siblingAtColumn(2).data(Qt.ItemDataRole.DisplayRole):
            option.features &= ~QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator

    def editorEvent(  # pylint: disable=invalid-name
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> bool:
        """
        When editing of an item starts, this function is called with the event that
        triggered the editing, the model, the index of the item, and the option used
        for rendering the item.

        Parameters
        ----------
        event : QEvent
            The event that triggered the editing.
        model : QAbstractItemModel
            The model for the item.
        option : QStyleOptionViewItem
            The option used for renderung the item.
        index : QModelIndex
            The index of the item.

        Returns
        -------
        bool
            If the event was handled.
        """

        if not self._is_leaf(index):
            return False
        return super().editorEvent(event, model, option, index)
