# -*- coding: utf-8 -*-
from __future__ import division
"""
/***************************************************************************
 GNSS_DOC_OPTIMIZERDockWidget
                                 A QGIS plugin
 Ground Network optimization for GNSS
                             -------------------
        begin                : 2016-12-11
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Mohamed Ali CHEBBI
        email                : Mohamed-Ali.Chebbi@ensg.eu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import numpy as np


# Paramètres de l'ellipsoîde IAG GRS 80 ASSOCIÉ AU RGF93
f = 1/298.257223563
e1_terrestre = np.sqrt(2*f-f**2)
a_terrestre = 6378137.0


import os
import re 
from PyQt4 import QtGui, uic, QtCore
from PyQt4.QtCore import pyqtSignal, SIGNAL, pyqtSlot, QRegExp

# Perform transformation between systems 
import Transform
import numpy as np
# call main code run_python
# import run_python
# Call Grd_ntwrk Module
from  Grd_ntwrk import Ground_network, Station
import GNSS_plugin 
from Add_station_Dialog_box import Add_stat_dbox

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'GNSS_plugin_dockwidget_base.ui'))



"""
class Rem_stat_dbox(QtGui.QDialog):
	def __init__(self):
		super(Rem_stat_dbox, self).__init__()
		# uic.loadUi(os.path.join(os.path.dirname(__file__),'dialog_box_addstation.ui'), self)
		# self.Remove_station.clicked.connect(self.accept)
		# self.Dismiss.clicked.connect(self.reject)
		
class Rem_stat_dbox(QtGui.QDialog):
	def __init__(self):
		super(add_stat_dbox, self).__init__()
		uic.loadUi(os.path.join(os.path.dirname(__file__),'dialog_box_addstation.ui'), self)
		self.Ok_add_station.clicked.connect(self.accept)
		self.Dismiss.clicked.connect(self.reject)
"""		
class GNSS_DOC_OPTIMIZERDockWidget(QtGui.QDockWidget, FORM_CLASS):

	closingPlugin = pyqtSignal()
	
	
	def __init__(self, gnss_plugin, parent=None):
		"""Constructor."""
		super(GNSS_DOC_OPTIMIZERDockWidget, self).__init__(parent)
		# Set up the user interface from Designer.
		# After setupUI you can access any designer object by doing
		# self.<objectname>, and you can use autoconnect slots - see
		# http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
		# #widgets-and-dialogs-with-auto-connect
		# self.add_dialog=Add_stat_dbox()
		# print(self.add_dialog)
		self.setupUi(self)
		self.Add_station.clicked.connect(self.addStation)
		self.gnss_plugin = gnss_plugin
		self.add_dialog=Add_stat_dbox()
		self.Remove_station.clicked.connect(self.removeStation)

	def addStation(self):
		#print(type(add_dialog),dir(add_dialog))
		transformneeded=True
		X_coord=0
		Y_coord=0
		Z_coord=0
		lam_coord=0
		fi_coord=0
		height_coord=0
		Name='station'
		if (self.add_dialog.exec_()==QtGui.QDialog.Accepted):
			reg_ex = QRegExp("[a-z-A-Z_]+")
			rgx=QtGui.QRegExpValidator(reg_ex)
			x_v=QtGui.QDoubleValidator(-1e7,1e7,15)
			y_v=QtGui.QDoubleValidator(-1e7,1e7,15)
			z_v=QtGui.QDoubleValidator(-1e7,1e7,15)
			self.add_dialog.name_station.setValidator(rgx)
			self.add_dialog.lineEdit_x_coord.setValidator(x_v)
			self.add_dialog.lineEdit_y_coord.setValidator(y_v)
			self.add_dialog.lineEdit_y_coord.setValidator(z_v)
			Name=self.add_dialog.name_station.text()
			if(self.add_dialog.Geocentric.isChecked()):
				transformneeded=True
				X_coord=self.add_dialog.lineEdit_x_coord.text()
				Y_coord=add_dialog.lineEdit_y_coord.text()
				Z_coord=self.add_dialog.lineEdit_z_coord.text()
				X_coord=np.double(X_coord)
				Y_coord=np.double(Y_coord)
				Z_coord=np.double(Z_coord)
			elif(self.add_dialog.Geographic.isChecked()):
				transformneeded=False
				lam_coord=self.add_dialog.lineEdit_x_coord.text()
				fi_coord=self.add_dialog.lineEdit_y_coord.text()
				height_coord=self.add_dialog.lineEdit_z_coord.text()
				lam_coord=np.double(lam_coord)
				fi_coord=np.double(fi_coord)
				height_coord=np.double(height_coord)
			else:
				print("not checked")
			if (transformneeded):
				trans=Transform.transform()
				lam_coord,fi_coord,height_coord=trans.transform2geog(X_coord,Y_coord,Z_coord,\
				e1_terrestre,f,a_terrestre)
				lam_coord=lam_coord*180.0/np.pi
				fi_coord=fi_coord*180.0/np.pi
				height_coord=height_coord*180.0/np.pi
			self.gnss_plugin.saveStation(Name,lam_coord,fi_coord,height_coord)
		self.add_dialog.done(QtGui.QDialog.Accepted)
		#Metod to remove a station directly from iface which is a QgsInterface instance
	def removeStation(self):
		self.gnss_plugin.remove_station()
	def closeEvent(self, event):
		self.closingPlugin.emit()
		event.accept()