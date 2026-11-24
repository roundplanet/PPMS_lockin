# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 12:57:30 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QTabWidget, QPushButton, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from .editable_tab_bar import EditableTabBar
from .daq_server_widget import DAQServerWidget

if TYPE_CHECKING:
    from .ppms_lockin_measurement_main_window import PPMSLockinMeasurementMainWindow


class DAQServerTabWidget(QTabWidget):
    """
    A subclass of QTabWidget, which will organize all individual DAQ servers and their widgets.

    Parameters
    ----------
    main_window : PPMSLockinMeasurementMainWindow
        The main window of the application.

    Attributes
    ----------
    main_window : PPMSLockinMeasurementMainWindow
        The main window of the application.

    """

    def __init__(self, main_window: PPMSLockinMeasurementMainWindow = None) -> None:
        super().__init__()
        self.main_window: PPMSLockinMeasurementMainWindow = main_window
        self.setTabBar(EditableTabBar(self))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.remove_tab)

        self.add_pb: QPushButton = QPushButton("  add DAQ server  ")
        self.add_pb.clicked.connect(self.add_tab)
        self.setCornerWidget(self.add_pb, Qt.Corner.TopRightCorner)
        self.add_tab()

    def add_tab(self) -> None:
        """
        Adds a DAQServerWidget to a new tab and connects the QLineEdit of the filename prefix from
        the main window with the QLineEdit of the final filename.

        Returns
        -------
        None
        """

        layout_widget: QWidget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(layout_widget)

        daq_server_widget: DAQServerWidget = DAQServerWidget()
        self.main_window.filename_prefix_le.textChanged.connect(
            daq_server_widget.update_filename_prefix
        )
        daq_server_widget.update_filename_prefix(self.main_window.filename_prefix_le.text())
        self.main_window.save_folder_le.textChanged.connect(daq_server_widget.update_save_folder)
        daq_server_widget.update_save_folder(self.main_window.save_folder_le.text())

        layout.addWidget(daq_server_widget)
        index: int = self.addTab(layout_widget, f"DAQ server {self.count() + 1}")
        self.setCurrentIndex(index)

    def remove_tab(self, index: int) -> None:
        """
        Removes the tab with the given index. If the last tab should be removed, a new tab will be
        added, so that at least one tab is open all the time.

        Parameters
        ----------
        index : int
            The index of the tab which sould be removed.

        Returns
        -------
        None
        """

        widget: QWidget = self.widget(index)
        self.removeTab(index)
        widget.deleteLater()
        if self.count() == 0:
            self.add_tab()
