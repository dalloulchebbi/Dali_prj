# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_box_addstation.ui'
#
# Created: Wed Jan 04 11:44:09 2017
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(412, 232)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 411, 231))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 30, 101, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(250, 30, 151, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.name_station = QtGui.QLineEdit(self.groupBox)
        self.name_station.setGeometry(QtCore.QRect(10, 60, 113, 20))
        self.name_station.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.name_station.setObjectName(_fromUtf8("name_station"))
        self.lineEdit_x_coord = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_x_coord.setGeometry(QtCore.QRect(20, 120, 111, 20))
        self.lineEdit_x_coord.setObjectName(_fromUtf8("lineEdit_x_coord"))
        self.lineEdit_y_coord = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_y_coord.setGeometry(QtCore.QRect(150, 120, 113, 20))
        self.lineEdit_y_coord.setObjectName(_fromUtf8("lineEdit_y_coord"))
        self.lineEdit_z_coord = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_z_coord.setGeometry(QtCore.QRect(282, 120, 111, 20))
        self.lineEdit_z_coord.setObjectName(_fromUtf8("lineEdit_z_coord"))
        self.condition_geographic = QtGui.QLabel(self.groupBox)
        self.condition_geographic.setGeometry(QtCore.QRect(10, 160, 391, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS PGothic"))
        font.setPointSize(11)
        self.condition_geographic.setFont(font)
        self.condition_geographic.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.condition_geographic.setObjectName(_fromUtf8("condition_geographic"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(10, 120, 21, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(140, 120, 16, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(270, 120, 21, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.Geographic = QtGui.QRadioButton(self.groupBox)
        self.Geographic.setGeometry(QtCore.QRect(250, 50, 82, 17))
        self.Geographic.setObjectName(_fromUtf8("Geographic"))
        self.Geocentric = QtGui.QRadioButton(self.groupBox)
        self.Geocentric.setGeometry(QtCore.QRect(250, 70, 82, 17))
        self.Geocentric.setObjectName(_fromUtf8("Geocentric"))
        self.Dismiss = QtGui.QPushButton(Dialog)
        self.Dismiss.setGeometry(QtCore.QRect(304, 200, 51, 23))
        self.Dismiss.setObjectName(_fromUtf8("Dismiss"))
        self.Ok_add_station = QtGui.QPushButton(Dialog)
        self.Ok_add_station.setGeometry(QtCore.QRect(364, 200, 41, 23))
        self.Ok_add_station.setObjectName(_fromUtf8("Ok_add_station"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.groupBox.setTitle(_translate("Dialog", "Enter station", None))
        self.label.setText(_translate("Dialog", "Name your station", None))
        self.label_2.setText(_translate("Dialog", "Give your system coordinates", None))
        self.condition_geographic.setText(_translate("Dialog", "If geographic chosen, X is longitude, Y is Latitude, Z is Height", None))
        self.label_3.setText(_translate("Dialog", "X:", None))
        self.label_4.setText(_translate("Dialog", "Y:", None))
        self.label_5.setText(_translate("Dialog", "Z:", None))
        self.Geographic.setText(_translate("Dialog", "Geographic", None))
        self.Geocentric.setText(_translate("Dialog", "Geocentric", None))
        self.Dismiss.setText(_translate("Dialog", "Dismiss", None))
        self.Ok_add_station.setText(_translate("Dialog", "OK", None))

