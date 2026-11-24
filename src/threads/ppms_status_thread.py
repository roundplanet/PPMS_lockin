# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 14:05:56 2026

@author: Administrator
"""

import threading
import time

import MultiPyVu as mpv

from .ppms_status_values import PPMSStatusValues


class PPMSStatusThread(threading.Thread):
    """
    A thread to retrieve the current status values from the PPMS like temperature or field.

    Parameters
    ----------
    interval : float
        The interval, in which the status of the PPMS is checked. The default is 0.1

    Attributes
    ----------
    ppms_status_values: PPMSStatusValues
        The object which will store the values of the current state of the PPMS.
    interval : float
        The interval, in which the status of the PPMS is checked.
    stop_event : threading.Event
        The event which will terminate the thread.
    """

    def __init__(self, interval: float = 0.1) -> None:
        super().__init__(daemon=True)
        self.ppms_status_values: PPMSStatusValues = PPMSStatusValues()
        self.interval: float = interval
        self.stop_event: threading.Event = threading.Event()

    def run(self):
        """
        Starts the thread, which will start the connection to MultiVu and retrieves the current
        status values from the PPMS.

        Returns
        -------
        None
        """

        with mpv.Server() as _:
            with mpv.Client() as client:
                while not self.stop_event.is_set():
                    start = time.time()
                    try:
                        temperature, _ = client.get_temperature()
                        time.sleep(0.01)
                        field, _ = client.get_field()
                        self.ppms_status_values.update({"temperature": temperature, "field": field})
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        print(f"Polling error: {e}")
                    self.stop_event.wait(self.interval - (time.time() - start))
