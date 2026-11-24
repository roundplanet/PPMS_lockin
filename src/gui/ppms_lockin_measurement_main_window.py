# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 16:04:28 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import os
import time
import json
from pathlib import Path
from dataclasses import asdict

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt


from .daq_server_tab_widget import DAQServerTabWidget
from ..threads.ppms_measurement_container_thread import PPMSMeasurementContainerThread
from ..threads.monitor_sequence_thread import MonitorSequenceThread
from ..session import Session, load_session_dataclass, create_session_dataclass

if TYPE_CHECKING:
    from PyQt6.QtCore import QEvent

    from .daq_server_widget import DAQServerWidget
    from ..data.mfli_leaf_node_info import MFLILeafNodeInfo

DATA_ROLE = Qt.ItemDataRole.UserRole
CHECKED = Qt.CheckState.Checked


class PPMSLockinMeasurementMainWindow(QMainWindow):  # pylint: disable=too-many-instance-attributes
    """
    A subclass of QMainWindow, which organzies the whole user interface and manages the interaction
    with the user.

    Attributes
    ----------
    starting_directories : dict[str, str]
        A dictionary which maps the filenames for the getOpenFileName dialogs towards their starting
        directory. If the user selects another file/folder in the dialog, the starting directory
        will be changed accordingly. The starting value is always the folder where the main function
        is or from where it is called from.
    sequence_filename : str
        The filename of the selected sequence, which will executed by MultiVu. There the user can
        insert a CHANGE_PREFIX remark with the new prefix after a space. If the real sequence passes
        this command, the application will change the saving .dat file accordingly.
    log_filename : str
        The filename of the logfile, which will be monitored by a thread and evaluated, at which
        position the sequence is at the moment.
    save_folder : str
        The folder in which the .dat file should be saved.
    daq_server_tab_widget : DAQServerTabWidget
        The widget which holds all DAQ servers in tabs.
    monitor_st : MonitorSequenceThread | None
        If the measurement is running, this thread checks the logfile for changes in the position
        of the sequence and handles the changes according to the remarks.
    ppms_mct : PPMSMeasurementContainerThread | None
        A container which will be filled with threads at the beginning of the measurement. Each
        thread is connected to a DAQ and saves its values according to the settings.
    measurement_paused : bool
        If the measurement is paused at the moment.
    measurement_prefix_change : bool
        If the prefix of the filename is changed at the moment.

    """

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(
            "/".join(os.path.abspath(__file__).split("\\")[:-1])
            + "/ui-files/ppms_lockin_measurement.ui",
            self,
        )

        self.starting_directories: dict[str, str] = {
            "sequence": "./",
            "logfile": "./",
            "save_folder": "./",
            "session": "./",
        }
        self.sequence_filename: str = ""
        self.log_filename: str = ""
        self.save_folder: str = ""
        self.sequence_browse_pb.clicked.connect(self.browse_sequence_filename)
        self.logfile_browse_pb.clicked.connect(self.browse_logfile_filename)
        self.save_folder_pb.clicked.connect(self.browse_save_folder)
        self.single_measurement_cb.clicked.connect(self.on_single_measurement)

        self.daq_server_tab_widget: DAQServerTabWidget = DAQServerTabWidget(self)
        self.daq_servers_vl.addWidget(self.daq_server_tab_widget)

        self.monitor_st: MonitorSequenceThread | None = None
        self.ppms_mct: PPMSMeasurementContainerThread | None = None
        self.measurement_paused: bool = False
        self.measurement_prefix_change: bool = False
        self.start_pb.clicked.connect(self.on_start)
        self.pause_pb.clicked.connect(self.on_pause)
        self.abort_pb.clicked.connect(self.on_abort)

        self.actionsave.triggered.connect(self.on_session_save)
        self.actionload.triggered.connect(self.on_session_load)

    def browse_sequence_filename(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        Opens a QFileDialog.getOpenFileName and asks the user for a new sequence filename. If the
        user selects another filename, the value will be changed and the starting directory as well.

        Parameters
        ----------
        event : TYPE
            The event emitted from the corresponding QPushButton.

        Returns
        -------
        None
        """

        self.sequence_filename: str = QFileDialog.getOpenFileName(
            self, "Open sequence file", self.starting_directories["sequence"], "*.seq"
        )[0]
        if self.sequence_filename == "":
            self.sequence_filename["sequence"]: str = "./"
        else:
            self.sequence_filename["sequence"]: str = "/".join(
                self.sequence_filename.split("/")[:-1]
            )
        self.sequence_le.setText(self.sequence_filename)

    def browse_logfile_filename(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        Opens a QFileDialog.getOpenFileName and asks the user for a new logfile filename. If the
        user selects another filename, the value will be changed and the starting directory as well.

        Parameters
        ----------
        event : TYPE
            The event emitted from the corresponding QPushButton.

        Returns
        -------
        None
        """

        self.log_filename: str = QFileDialog.getOpenFileName(
            self, "Open logfile", self.starting_directories["logfile"], "*.dat"
        )[0]
        if self.log_filename == "":
            self.starting_directories["logfile"]: str = "./"
        else:
            self.starting_directories["logfile"]: str = "/".join(self.log_filename.split("/")[:-1])
        self.logfile_le.setText(self.log_filename)

    def browse_save_folder(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        Opens a QFileDialog.getOpenFileName and asks the user for a new save folder. If the
        user selects another filename, the value will be changed and the starting directory as well.

        Parameters
        ----------
        event : TYPE
            The event emitted from the corresponding QPushButton.

        Returns
        -------
        None
        """

        save_folder: str = QFileDialog.getExistingDirectory(
            self, "Open save_folder", self.starting_directories["save_folder"]
        )
        if save_folder == "" and self.save_folder != "":
            self.starting_directories["save_folder"]: str = "./"
        else:
            self.save_folder: str = save_folder
            self.starting_directories["save_folder"]: str = save_folder
        self.save_folder_le.setText(self.save_folder)

    def on_single_measurement(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        If the user selects the single measurement option, the sequence and logfile becomes
        irrelevant. Therefore these entries will be turned off, otherwise they will be clickable
        again.

        Parameters
        ----------
        event : QEvent
            The event emitted from the corresponding QCheckBox.

        Returns
        -------
        None
        """

        self.sequence_le.setEnabled(not event)
        self.sequence_browse_pb.setEnabled(not event)
        self.logfile_le.setEnabled(not event)
        self.logfile_browse_pb.setEnabled(not event)

    def change_prefix(self, new_prefix: str) -> None:
        """
        Changes the prefix of the filename for the .dat file. Therefore the measurement will be
        terminated, the prefix will be changed and after a short sleep the measurement will be
        started again.

        Parameters
        ----------
        new_prefix : str
            The new prefix to be set.

        Returns
        -------
        None
        """

        print("in change_prefix")
        self.measurement_prefix_change: bool = True
        self.on_abort(None)
        self.filename_prefix_le.setText(new_prefix)
        time.sleep(0.25)
        self.on_start(None)
        self.measurement_prefix_change: bool = False
        print("out of change_prefix")

    def on_start(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        Starts the measurement by iterating over all configure DAQ severs and starting the
        measurement threads.

        Parameters
        ----------
        event : QEvent
            The event emitted from the corresponding QPushButton.

        Returns
        -------
        None
        """

        self.start_pb.setEnabled(False)
        self.pause_pb.setEnabled(True)
        self.abort_pb.setEnabled(True)
        if not self.single_measurement_cb.isChecked() and not self.measurement_prefix_change:
            self.monitor_st: MonitorSequenceThread = MonitorSequenceThread(self)
            self.monitor_st.start()
        self.ppms_mct: PPMSMeasurementContainerThread = PPMSMeasurementContainerThread(
            self.daq_server_tab_widget
        )
        self.ppms_mct.start()

    def on_pause(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        If the user clicks on the button labled pause, the measurement will be paused and the text
        on the button changes to continue. If the user clicks again, the measurement will be
        continued.

        Parameters
        ----------
        event : QEvent
            The event emitted from the corresponding QPushButton.

        Returns
        -------
        None
        """

        if self.measurement_paused:
            self.ppms_mct.sleep_event.clear()
            self.measurement_paused: bool = False
            self.pause_pb.setText("pause")
        else:
            self.ppms_mct.sleep_event.set()
            self.measurement_paused: bool = True
            self.pause_pb.setText("continue")

    def on_abort(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        Aborts the measurement and closes all measurement threads.

        Parameters
        ----------
        event : QEvent
            The event emitted from the corresponding QPushButton.

        Returns
        -------
        None
        """

        if self.ppms_mct is not None:
            self.ppms_mct.stop_event.set()
            self.ppms_mct.join()
            self.ppms_mct: None = None
            if not self.single_measurement_cb.isChecked() and not self.measurement_prefix_change:
                self.monitor_st.stop_event.set()
            self.start_pb.setEnabled(True)
            self.measurement_paused: bool = False
            self.pause_pb.setEnabled(False)
            self.pause_pb.setText("pause")
            self.abort_pb.setEnabled(False)

    def closeEvent(self, event: QEvent) -> None:  # pylint: disable=invalid-name,unused-argument
        """
        Overrides the original function, because if the window closes and a measurement is still
        running, this has to be aborted first.

        Parameters
        ----------
        event : QEvent
            The event emitted from the corresponding QMainWidget.

        Returns
        -------
        None
        """

        self.on_abort(None)
        event.accept()

    def on_session_save(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        Saves the session in a .json file at the chosen directory.

        Parameters
        ----------
        event : QEvent
            The event emitted from the corresponding QAction.

        Returns
        -------
        None
        """

        session_filename: str = QFileDialog.getSaveFileName(
            self, "Save session", self.starting_directories["session"], "*.json"
        )[0]
        if session_filename == "":
            return
        self.starting_directories["session"]: str = "/".join(session_filename.split("/")[:-1])

        session: Session = create_session_dataclass(self)

        with open(session_filename, "w", encoding="utf-8") as file:
            json.dump(asdict(session), file, indent=2)

    def on_session_load(self, event: QEvent) -> None:  # pylint: disable=unused-argument
        """
        Loads a session in a .json file from the chosen directory.

        Parameters
        ----------
        event : QEvent
            The event emitted from the corresponding QAction.

        Returns
        -------
        None
        """
        reply = QMessageBox.warning(
            self,
            "Load session",
            "Loading a session will replace all current settings.\n"
            "Unsaved changes will be lost. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        session_filename: str = QFileDialog.getOpenFileName(
            self, "Load session", self.starting_directories["session"], "*.json"
        )[0]
        if session_filename == "":
            return
        self.starting_directories["session"]: str = "/".join(session_filename.split("/")[:-1])

        data = json.loads(Path(session_filename).read_text(encoding="utf-8"))
        session: Session = Session.from_dict(data)

        for _ in range(self.daq_server_tab_widget.count()):
            self.daq_server_tab_widget.remove_tab(0)

        load_session_dataclass(self, session)
