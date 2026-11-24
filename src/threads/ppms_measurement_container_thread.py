# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 16:23:09 2026

@author: Administrator
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import threading
import time

from .ppms_status_thread import PPMSStatusThread
from .ppms_measurement_thread import PPMSMeasurementThread

if TYPE_CHECKING:
    from ..gui.daq_server_tab_widget import DAQServerTabWidget
    from ..gui.daq_server_widget import DAQServerWidget


class PPMSMeasurementContainerThread(threading.Thread):
    """
    A thread to handle all individual measurement threads from the DAQ servers in the different tabs
    from the main window. Keeps his sleep and stop event syncronized with the events from the
    individual measurements.

    Parameters
    ----------
    daq_server_tab_widget: DAQServerTabWidget
        The widget which holds all tabs with the information about the corresponding DAQ server
        and saving process.

    Attributes
    ----------
    daq_server_tab_widget: DAQServerTabWidget
        The widget which holds all tabs with the information about the corresponding DAQ server
        and saving process.
    stop_event : threading.Event
        The event which will terminate the thread.
    was_sleeping : bool
        If the thread is sleeping at the moment.
    sleep_event : threading.Event
        The event which will get the thread to temporarily stop.
    ppms_status_thread : PPMSStatusThread
        The thread which will keep the PPMS status up to date.
    measurement_threads: list[PPMSMeasurementThread]
        The list of measurement threads, which the container can start.
    """

    def __init__(self, daq_server_tab_widget: DAQServerTabWidget) -> None:
        super().__init__(daemon=True)
        self.daq_server_tab_widget: DAQServerTabWidget = daq_server_tab_widget

        self.stop_event: threading.Event = threading.Event()
        self.was_sleeping: bool = False
        self.sleep_event: threading.Event = threading.Event()

        self.ppms_status_thread: PPMSStatusThread = PPMSStatusThread()
        self.measurement_threads: list[PPMSMeasurementThread] = []

        for index in range(self.daq_server_tab_widget.count()):
            w: DAQServerWidget = (
                self.daq_server_tab_widget.widget(index).layout().itemAt(0).widget()
            )
            if w.connected:
                self.measurement_threads.append(
                    PPMSMeasurementThread(w, self.ppms_status_thread.ppms_status_values)
                )

    def run(self) -> None:
        """
        Starts the thread, which will starts all threads in the container and sets the stop and
        sleep event of the threads in the container accordint to its own events.

        Returns
        -------
        None
        """

        self.ppms_status_thread.start()
        time.sleep(0.5)
        for thread in self.measurement_threads:
            thread.start()

        while not self.stop_event.is_set():
            if not self.sleep_event.is_set():
                if self.was_sleeping:
                    self.was_sleeping: bool = False
                    for thread in self.measurement_threads:
                        thread.sleep_event.clear()
                    time.sleep(0.25)
                else:
                    time.sleep(0.25)
            else:
                if self.was_sleeping:
                    time.sleep(0.25)
                else:
                    self.was_sleeping: bool = True
                    for thread in self.measurement_threads:
                        thread.sleep_event.set()
                    time.sleep(0.25)

        for thread in self.measurement_threads:
            thread.stop_event.set()
        for thread in self.measurement_threads:
            thread.join()
        self.ppms_status_thread.stop_event.set()
        self.ppms_status_thread.join()
