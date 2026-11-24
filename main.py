# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 16:06:03 2026

@author: Administrator
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication

from src.gui.ppms_lockin_measurement_main_window import PPMSLockinMeasurementMainWindow

logging.disable(logging.CRITICAL)

app = QApplication(sys.argv)
w = PPMSLockinMeasurementMainWindow()
w.show()
app.exec()
sys.exit()