# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 12:46:33 2026

@author: Administrator
"""

from PyQt6.QtWidgets import QTabBar, QWidget
from PyQt6.QtCore import QEvent

from .tab_name_editor_line_edit import TabNameEditorLineEdit


class EditableTabBar(QTabBar):
    """
    A subclass of QTabBar, which will create a QLineEdit at the tab name position after a double
    click, so the user can change the name of the tab.

    Parameters
    ----------
    parent : QWidget | None
        The parent widget of the class.

    Attributes
    ----------
    editor : None | TabNameEditorLineEdit
        The TabNameEditorLineEdit which will be created after the double click to the tabs name.
    tab_index : int
        The index of the tab where the user clicked.

    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.editor: None | TabNameEditorLineEdit = None
        self.tab_index: int = -1

    def mouseDoubleClickEvent(self, event: QEvent) -> None:  # pylint: disable=invalid-name
        """
        Reimplements the behaviour of the widget after a double mouse click.

        Parameters
        ----------
        event : QEvent
            The event form the double click.

        Returns
        -------
        None
        """

        tab_index: int = self.tabAt(event.position().toPoint())
        if tab_index < 0:
            super().mouseDoubleClickEvent(event)
        self.commit_changes()
        self.tab_index: int = tab_index
        self.editor: TabNameEditorLineEdit = TabNameEditorLineEdit(self.tabText(tab_index), self)
        self.editor.setGeometry(self.tabRect(tab_index))
        self.editor.editingFinished.connect(self.commit_changes)
        self.editor.show()
        self.editor.selectAll()
        self.editor.setFocus()

    def commit_changes(self) -> None:
        """
        After the editing is finished on the editor, the name of the tab is changed.

        Returns
        -------
        None
        """

        editor, self.editor = self.editor, None
        if editor is None:
            return
        text: str = editor.text().strip()
        if text and 0 <= self.tab_index < self.count():
            self.setTabText(self.tab_index, text)
        editor.deleteLater()
