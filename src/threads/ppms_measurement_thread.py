# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 10:20:07 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import time
import threading

from ..data.multi_vu_data_file_handler import MultiVuDataFileHandler

if TYPE_CHECKING:
    from .ppms_status_values import PPMSStatusValues
    from ..gui.daq_server_widget import DAQServerWidget


class PPMSMeasurementThread(threading.Thread):
    """
    A thread to perform a measurement by retrieving data in a fixed interval from a data server from
    the corresponding DAQ server and save the data to the given MultiVu .dat file.

    Parameters
    ----------
    daq_server_widget: DAQServerWidget
        The widgets which hold all the information about the DAQ server and the saving process.
    ppms_status_values : PPMSStatusValues
        The object from which the thread can get the current status of the PPMS values like
        temperature or field.

    Attributes
    ----------
    daq_server_widget: DAQServerWidget
        The widgets which hold all the information about the DAQ server and the saving process.
    ppms_status_values : PPMSStatusValues
        The object from which the thread can get the current status of the PPMS values like
        temperature or field.
    sampling_rate : float
        The time between to calls from the DAQ server.
    stop_event : threading.Event
        The event which will terminate the thread.
    was_sleeping : bool
        If the thread is sleeping at the moment.
    sleep_event : threading.Event
        The event which will get the thread to temporarily stop.
    multi_vu_dfh : MultiVuDataFileHandler
        The object which will handle the retrieving and saving of the data from the data server and
        saving it to a .dat file.
    """

    def __init__(
        self, daq_server_widget: DAQServerWidget, ppms_status_values: PPMSStatusValues
    ) -> None:
        super().__init__(daemon=True)
        self.daq_server_widget: DAQServerWidget = daq_server_widget
        self.ppms_status_values: PPMSStatusValues = ppms_status_values
        self.sampling_rate: float = self.daq_server_widget.sampling_rate_dsb.value()
        self.stop_event: threading.Event = threading.Event()
        self.was_sleeping: bool = False
        self.sleep_event: threading.Event = threading.Event()
        print(self.daq_server_widget.filename_le.text())
        self.multi_vu_dfh: MultiVuDataFileHandler = MultiVuDataFileHandler(
            self.daq_server_widget.filename_le.text(),
            self.ppms_status_values,
            self.daq_server_widget.daq,
            list(self.daq_server_widget.streaming_nodes_table.generate_save_dict().keys()),
            self.daq_server_widget.generate_std_list(),
            self.daq_server_widget.generate_len_list(),
            list(self.daq_server_widget.header_nodes_table.generate_save_dict().keys()),
            self.daq_server_widget.generate_save_dict(),
            save_temperature=self.daq_server_widget.temperature_cb.isChecked(),
            save_field=self.daq_server_widget.field_cb.isChecked(),
            save_rotator=self.daq_server_widget.rotator_pos_cb.isChecked(),
        )

        self.multi_vu_dfh.configure_daq()
        self.multi_vu_dfh.create_file()

    def run(self) -> None:
        """
        Starts the thread, which will first sync the DAQ server, then starts to acquire the data
        for the data server and waits until the defined time has passed to start the cycle again.
        It also listens to the sleep and stop event and handles it.

        Returns
        -------
        None
        """

        self.daq_server_widget.daq.sync()
        while not self.stop_event.is_set():
            if not self.sleep_event.is_set():
                if self.was_sleeping:
                    self.daq_server_widget.daq.sync()
                    self.was_sleeping: bool = False
                start = time.time()
                try:
                    self.multi_vu_dfh.acquire_data(self.sampling_rate)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Measurement Thread error: {e}")
                time_to_wait: float = self.sampling_rate - (time.time() - start)
                if time_to_wait > 0:
                    self.stop_event.wait(time_to_wait)
            else:
                self.was_sleeping: bool = True
                time.sleep(0.25)
