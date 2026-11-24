# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 14:00:53 2026

@author: Administrator
"""

import threading


class PPMSStatusValues:
    """
    A thread-save object to store the current status of the PPMS.

    Attributes
    ----------
    lock : threading.Lock
        Ensures that two processes won't interfere with each other when accessing this object.
    values : dict[str, float]
        The current status values of the PPMS.
    """

    def __init__(self) -> None:
        self.lock: threading.Lock = threading.Lock()
        self.values: dict[str, float] = {
            "temperature": None,
            "field": None,
            "rotator position": None,
        }

    def update(self, update_dict: dict[str, float]) -> None:
        """
        Updates the values with the given dictionary.

        Parameters
        ----------
        update_dict : dict[str, float]
            The dictionary with the new values.

        Returns
        -------
        None
        """

        with self.lock:
            self.values.update(update_dict)

    def get(self, name: str) -> float:
        """
        Gets the value of the given name.

        Parameters
        ----------
        name : str
            The name of the value which should be get.

        Returns
        -------
        float
            The value of the given name.
        """

        with self.lock:
            return self.values[name]

    def snapshot(self) -> dict[str, float]:
        """
        Returns a new dictionary with the current values.

        Returns
        -------
        dict[str, float]
            The dictionary with the current values.
        """

        with self.lock:
            return dict(self.values)
