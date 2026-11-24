# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:55:29 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import os
import threading

if TYPE_CHECKING:
    from ..gui.ppms_lockin_measurement_main_window import PPMSLockinMeasurementMainWindow


class MonitorSequenceThread(threading.Thread):  # pylint: disable=too-many-instance-attributes
    """
    A thread to monitor the sequence executing by the PPMS by checking the state/line of the
    sequence via the active logfile. If the user includes a 'CHANGE_PREFIX' remark in the sequence,
    the thread recognizes and changes the filename with the correct prefix. If the sequence has
    terminated, the thread will recognize this and abort the measurement.

    Parameters
    ----------
    main_window : PPMSLockinMeasurementMainWindow
        The main window of the application.

    Attributes
    ----------
    main_window : PPMSLockinMeasurementMainWindow
        The main window of the application.
    sequence_filename : str
        The filename of the sequence, which should be measured.
    log_filename : str
        The filename of the logfile, which should be monitored for changes in the sequence line.
    seq_stat_index : int
        The index of the column, to where the sequence status is written in the logfile.
    prefix_list : list[str]
        A list of prefix filenames, corresponding to which prefix should be present at the given
        sequence line.
    current_seq_line : int
        The current sequence line, at which the sequence is.
    current_seq_status : int
        The status of the sequence at the moment. Either it is idle (0) or executing/waiting for
        completion (1 or 2)
    current_seq_prefix : str
        The current prefix.
    measurement_started : bool
        If the measurement has already started.
    amount_of_idle_calls : int
        How many calls were idle in a row.
    """

    def __init__(self, main_window: PPMSLockinMeasurementMainWindow) -> None:
        super().__init__(daemon=True)
        self.main_window: PPMSLockinMeasurementMainWindow = main_window
        self.sequence_filename: str = self.main_window.sequence_filename
        self.log_filename: str = self.main_window.log_filename

        self.seq_stat_index: int = self.get_seq_stat_index()
        self.prefix_list: list[str] = self.get_prefix_list()
        self.current_seq_line: int = 0
        self.current_seq_status: int = 0
        self.current_seq_prefix: str = self.main_window.filename_prefix_le.text()
        self.measurement_started: bool = False
        self.amount_of_idle_calls: int = 0

        self.stop_event: threading.Event = threading.Event()

    def get_seq_stat_index(self) -> int:
        """
        Returns the index of the 'Seq Stat ()' column in the header of the .dat file.

        Returns
        -------
        int
            The index of the column for the sequence status.
        """

        with open(self.log_filename, "r", encoding="utf-8") as f:
            next_is_data_line: bool = False
            for line in f:
                if next_is_data_line:
                    index: str = line.split(",").index("Seq Stat ()")
                    return index
                if line.startswith("[Data]"):
                    next_is_data_line = True
        return -1

    def get_prefix_list(self) -> list[str]:
        """
        Generates a list for each executable line in the sequence. It starts with the defined
        filename in the main window and repeats that, until a 'CHANGE_PREFIX' command appears in the
        sequence.

        Returns
        -------
        list[str]
            The list containing the filename for the .dat file for each executable sequence line.
        """

        prefix: str = self.main_window.filename_prefix_le.text()
        prefixes: list[str] = []

        with open(self.sequence_filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("REM"):
                    if line.split(" ")[1] == "CHANGE_PREFIX":
                        new_prefix: str = line.split(" ")[2]
                        if new_prefix[-1] == "\n":
                            new_prefix: str = new_prefix[:-1]
                        prefix: str = new_prefix
                elif line.startswith("!"):
                    pass
                else:
                    prefixes.append(prefix)
        prefixes.append(
            prefix
        )  # Sequence always ends with 'End Sequence', there the file prefix shouldn't change
        return prefixes

    def evaluate_line(self, line: str) -> None:
        """
        Evaluates a given line of the logfile. If the status has not changed from 0 (idle) the last
        ten calls, it is assumed, that the sequence is done and the measurement will be aborted.
        If not, then it is checked if the sequence has gone to the next line and checked, if the
        filename has to be changed.

        Parameters
        ----------
        line : str
            The line from the logfile which has to be evaluated.

        Returns
        -------
        None
        """

        value: float = float(line.split(b",")[self.seq_stat_index])
        seq_line: int = int(str(value).split(".")[0])  # pylint: disable=use-maxsplit-arg
        status: int = int(str(value).split(".")[1])
        if not self.measurement_started:
            if status != 0:
                self.measurement_started: bool = True
                return
        else:
            if status == 0:
                self.amount_of_idle_calls += 1
                if self.amount_of_idle_calls > 10:
                    self.main_window.on_abort(None)
                    return
                return
            self.amount_of_idle_calls: int = 0
            prefix: str = self.prefix_list[seq_line - 1]
            if prefix != self.current_seq_prefix:
                self.main_window.change_prefix(prefix)
                self.current_seq_prefix: str = prefix

    def run(self) -> None:
        """
        Starts the thread, which will check every 0.25 s for a new line in the logfile and evaluates
        it if it is present.

        Returns
        -------
        None
        """

        offset: int = os.path.getsize(self.log_filename)
        buf: bytes = b""
        while not self.stop_event.is_set():
            size: int = os.path.getsize(self.log_filename)
            if size > offset:
                with open(self.log_filename, "rb") as f:
                    f.seek(offset)
                    chunk: bytes = f.read()
                offset += len(chunk)
                *lines, buf = (buf + chunk).split(b"\n")  # last piece may be an incomplete line
                for line in lines:
                    self.evaluate_line(line)
            self.stop_event.wait(0.25)
