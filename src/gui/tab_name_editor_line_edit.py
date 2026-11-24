# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 12:43:14 2026

@author: Administrator
"""

from PyQt6.QtWidgets import QLineEdit, QWidget
from PyQt6.QtCore import Qt, QEvent


class TabNameEditorLineEdit(QLineEdit):
    """
    A subclass of QLineEdit, which will handle the renaming of a tab in the QTabView.

    Parameters
    ----------
    text : str
        The orginal text of the field.
    parent : QWidget
        The parent of this widget.

    Attributes
    ----------
    original_text : str
        The original text of the field.

    """

    def __init__(self, text: str, parent: QWidget) -> None:
        super().__init__(text, parent)
        self.original_text: str = text

    def keyPressEvent(self, event: QEvent) -> None:  # pylint: disable=invalid-name
        """
        Adds to the parent keyPressEvent, that if the user hits the escape key, the edit is done.

        Parameters
        ----------
        event : QEvent
            The emitted event.

        Returns
        -------
        None
        """

        if event.key() == Qt.Key.Key_Escape:
            self.setText(self.original_text)
            self.editingFinished.emit()
        else:
            super().keyPressEvent(event)
