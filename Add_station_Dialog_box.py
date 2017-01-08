# -*- coding: utf-8 -*-	
import os
from PyQt4 import QtGui, uic, QtCore
from PyQt4.QtCore import pyqtSignal, SIGNAL, pyqtSlot

# Class that usues the QDialog made using QtDesigner 

class Add_stat_dbox(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.ui=uic.loadUi(os.path.join(os.path.dirname(__file__),'dialog_box_addstation.ui'), self)
		self.ui.Ok_add_station.clicked.connect(self.accept)
		self.ui.Dismiss.clicked.connect(self.reject)
		# Save reference to the QGIS interface
	def __del__(self):
		print("deleted")