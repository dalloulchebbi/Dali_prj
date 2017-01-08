
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class SelectTool(QgsMapToolIdentify):
	def __init__(self, face):
		self.face = face
		QgsMapToolIdentify.__init__(self, face.mapCanvas())
		self.setCursor(Qt.ArrowCursor)
	def canvasReleaseEvent(self, event):
		found_features = self.identify(event.x(), event.y(),
		self.TopDownStopAtFirst,
		self.VectorLayer)
		if len(found_features) > 0:
			layer = found_features[0].mLayer
			feature = found_features[0].mFeature
			if event.modifiers() & Qt.ShiftModifier:
				layer.select(feature.id())
			else:
				layer.setSelectedFeatures([feature.id()])
		else:
			self.face.layer.removeSelection()
	def __del__(self):
		print("deleted")