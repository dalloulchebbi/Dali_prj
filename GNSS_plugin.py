# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GNSS_DOC_OPTIMIZER
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QVariant
from PyQt4.QtGui import QAction, QIcon, QColor, QMessageBox
# Initialize Qt resources from file resources.py
import resources
# Import the code for the DockWidget
from GNSS_plugin_dockwidget import GNSS_DOC_OPTIMIZERDockWidget

#******Import dialog box for adding a station
# from add_station import Ui_Dialog

import os
# import run_python
import re
import numpy as np

from qgis.core import *
from qgis.gui import *
from qgis.analysis import *


import GPSTIME as gpst
import time
import constell
import Transform
import Transform2
from Grd_ntwrk import Ground_network, Station


# Importing tools to manage user interaction with the QgsInterface
from selectTool import SelectTool


#==========================================================
# Paramètres de l'ellipsoîde IAG GRS 80 ASSOCIÉ AU RGF93
f = 1/298.257223563
e1_terrestre = np.sqrt(2*f-f**2)
a_terrestre = 6378137.0
# =========================================================
# Vitesse angulaire de rotation terrestre en rad/s
omegapoint = -7.2921151467e-5
# =========================================================
xc = 0.0
yc =0.0
n = 6378137.0
#=============================================================
# Définition des instances GPS, GLONASS, BEIDOU, GALILEO
#=============================================================
gps=os.path.join(os.path.dirname(__file__), 'gps_tle.dat')
glo=os.path.join(os.path.dirname(__file__), 'glonass_tle.dat')
gal=os.path.join(os.path.dirname(__file__), 'galileo_tle.dat')
bei=os.path.join(os.path.dirname(__file__), 'beidou_tle.dat')

file_name=[gps,glo,gal,bei]

Constellation_GPS=constell.Constellation('GPS')
Constellation_GLONASS=constell.Constellation('GLONASS')
Constellation_GALILEO=constell.Constellation('GALILEO')
Constellation_BEIDOU=constell.Constellation('BEIDOU')
#===========================================================
# Lecture des fichiers Norad
# Enregistrement des données nécessaires pour la détermination
# des positions des satellites de chaque constellation
#===========================================================

Constellation_GPS.retrieve_data_from_filename(file_name[0])
Constellation_GLONASS.retrieve_data_from_filename(file_name[1])
Constellation_GALILEO.retrieve_data_from_filename(file_name[2])
Constellation_BEIDOU.retrieve_data_from_filename(file_name[3])


#===========================================================
# Calcul de la position actuelle de la constellation satellitale
# en question
#===========================================================

Constellation_GPS.get_constellation_position()
Constellation_GLONASS.get_constellation_position()
Constellation_BEIDOU.get_constellation_position()
Constellation_GALILEO.get_constellation_position()

#======================================================
# Stations REGINA issues du réseau IGS sur Internet
#======================================================
Stations_Regina=[\
['LES ABYMES',[16.2622222,-61.5275000,-25.0]],\
['DAEJEON',[36.3991667,127.3744444,117.037]],\
['AJACCIO',[41.9272222,8.7625000,99.0]],\
#['AREQUIPA',[-16.4652778,-71.4927778,2489.337]],\
#['CIBINONG',[-6.4900000,106.8500000,158.18]],\
['BREST',[48.3802778,-4.4963889,65.8]],\
['CACHOEIRA',[-22.6822222,-45.0022222,566.250]],\
#['ASCENSION ISLAND',[-14.3325000,-7.9161111,37.953]],\
['ESPARGOS',[16.7319444,-22.9347222,94.089]],\
['DJIBOUTI',[11.5261111,42.8469444,711.409]],\
['DIONYSOS',[38.0783333,23.9322222,510.6]],\
['RIKITEA',[-23.1302778,-134.9647222,80.660]],\
['PRETORIA',[-25.8869444,27.7072222,1558.078]],\
['JIUFENG',[30.5155556,114.4908333,71.324]],\
['KITAB',[39.1333333,66.8866667,622.1]],\
['KOUROU',[5.0983333,-52.6397222,107.248]],\
['KERGUELEN',[-49.3513889,70.2552778,72.9673]],\
['LE LAMENTIN',[14.5947222,-60.9961111,-27.0]],\
['DZAOUDZI',[-12.7819444,45.2580556,-16.35]],\
['LIBREVILLE',[0.3538889,9.6719444,31.496]],\
['NOUMEA',[-22.2280556,166.4847222,160.384]],\
['OWENGA',[-44.0241667,-176.3686111,21.603]],\
['MANILLE',[14.5352778,121.0411111,86.944]],\
['RIO GRANDE',[-53.7858333,-67.7513889,32.364]],\
['MAHE',[-4.6786111,55.5305556,-37.085]],\
['ST.JOHN''\'''S',[47.5952778,-52.6780556,154.515]],\
['PAPEETE',[-17.5769444,-149.6063889,97.994]],\
['TOULOUSE',[43.5605556,1.4808333,207.2]],\
['YELLOWKNIFE',[62.4811111,-114.4808333,181.008]],\
['FUTUNA',[-14.3077778,-178.1208333,84.859]],\
['CROZET',[-46.4316667,51.8552778,202.8]],\
['GRASSE',[43.7547222,6.9205556,1319.3]],\
['METSAHOVI',[60.2419444,24.3841667,59.672]]]

# Instantiate Ground_Network Class to create Regina
Regina=Ground_network()

# Add_stations to Regina 

for t in Stations_Regina:
	St=Station(t[0],t[1])
	St.calculate_visiblilty_conic()
	# print(St.visibility_conic)
	Regina.add_station(St)
# Regina=Grd_ntwrk.Ground_network(Stations_Regina)
# print(Regina.stations)

class GNSS_DOC_OPTIMIZER:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.Regina=None
        # Save reference to the QGIS interface
        self.iface = iface
        # Create 4 vectors layers that will be changed accroding 
        # to different events
        self.vect_map=None
        self.vect_grd=None
        self.vect_cover=None
        self.vect_sky=None
        self.vect_doc=None
        self.selectTool=None
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GNSS_DOC_OPTIMIZER_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GNSS_DOC')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GNSS_DOC_OPTIMIZER')
        self.toolbar.setObjectName(u'GNSS_DOC_OPTIMIZER')

        #print "** INITIALIZING GNSS_DOC_OPTIMIZER"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GNSS_DOC_OPTIMIZER', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setCheckable(True)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GNSS_DOC_OPTIMIZER/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Gnss'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING GNSS_DOC_OPTIMIZER"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crash
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD GNSS_DOC_OPTIMIZER"

        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&GNSS_DOC'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
		"""Run method that loads and starts the plugin"""

		if not self.pluginIsActive:
			self.pluginIsActive = True

			#print "** STARTING GNSS_DOC_OPTIMIZER"

			# dockwidget may not exist if:
			#    first run of plugin
			#    removed on close (see self.onClosePlugin method)
			if self.dockwidget == None:
				# Create the dockwidget (after translation) and keep reference
				self.dockwidget = GNSS_DOC_OPTIMIZERDockWidget(self)
			# connect to provide cleanup on closing of dockwidget
			self.dockwidget.closingPlugin.connect(self.onClosePlugin)

			# show the dockwidget
			# TODO: fix to allow choice of dock location
			self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
			self.dockwidget.show()
			self.Regina=Ground_network()
			# Add_stations to Regina 
			for t in Stations_Regina:
				St=Station(t[0],t[1])
				St.calculate_visiblilty_conic()
				# print(St.visibility_conic)
				self.Regina.add_station(St)
			self.vect_map=QgsVectorLayer(os.path.join(os.path.dirname(__file__),'mapp.shp'),"Earth","ogr")
			self.vect_grd=QgsVectorLayer('Point?crs=epsg:4326&index=yes','Grd_network',"memory")
			self.vect_cover=QgsVectorLayer('Polygon?crs=epsg:4326&index=yes','Vector',"memory")
			self.vect_sky=QgsVectorLayer('Polygon?crs=epsg:4326&index=yes','constell',"memory")
			self.vect_doc=QgsVectorLayer('Polygon?crs=epsg:4326&index=yes','doc',"memory")
			#instantiate selection tool 
			# self.selectTool=SelectTool(self)
		self.construct_vect_layers()
		
    def construct_vect_layers(self):
		# Delete all vectorlayers appearing in the iface
		# layer_registry = QgsMapLayerRegistry.instance()
		# layer_registry.removeAllMapLayers()
		mc=self.iface.mapCanvas()
		pr=self.vect_cover.dataProvider()
		grd_pr=self.vect_grd.dataProvider()
		pr.addAttributes([QgsField("name", QVariant.String),
		QgsField("order", QVariant.Int)])
		grd_pr.addAttributes([QgsField("grd_name", QVariant.String)])
		self.vect_cover.startEditing()
		self.vect_grd.startEditing()
		j=0
		# print(len(self.Regina.stations))
		for station in self.Regina.stations:
			ptt=station.visibility_conic
			# print(station.visibility_conic)
			poly_pt=[]
			# print(len(ptt[0][0]))
			# print(QgsPoint(ptt[0][0][0],ptt[0][1][0]))
			for i in xrange(len(ptt[0][0])):
				poly_pt+=[QgsPoint(ptt[0][0][i],ptt[0][1][i])]
			poly_pt.append(QgsPoint(ptt[0][0][0],ptt[0][1][0]))
			# Instantiate features 
			visib=QgsFeature()
			grd_feat=QgsFeature()
			visib.setGeometry(QgsGeometry.fromPolygon([poly_pt]))
			visib.setAttributes([station.Name,j])
			# =======================================
			grd_feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(station.Coords[1],\
			station.Coords[0])))
			grd_feat.setAttributes([station.Name])
			# Now add features to providers
			pr.addFeatures([visib])
			grd_pr.addFeatures([grd_feat]) 
			self.vect_cover.setLayerTransparency(80)
			self.vect_cover.updateExtents()
			self.vect_grd.updateExtents()
			#symbols = self.rendererV2().symbols()
			#symbol = symbols[0]
			#symbol.setColor(QColor.fromRgb(200,5*j,200))
			j+=1
		self.vect_cover.commitChanges()
		self.vect_grd.commitChanges()
#==============================================================
		# Labeling the grd network Points
		p = QgsPalLayerSettings()
		p.readFromLayer(self.vect_grd)
		p.enabled = True
		p.fieldName = "grd_name"
		p.placement = QgsPalLayerSettings.OverPoint
		p.displayAll = True
		p.setDataDefinedProperty(QgsPalLayerSettings.Size,\
		True, True, "12", "")
		p.quadOffset = QgsPalLayerSettings.QuadrantBelow
		p.yOffset = 1
		p.labelOffsetInMapUnits = False
		p.writeToLayer(self.vect_grd)
		labelingEngine = QgsPalLabeling()
		mc.mapRenderer().setLabelingEngine(labelingEngine)
#==============================================================
		# Call to algorithm: DOC calulation using QgsGeometry methods 
		# fot topological operations 
		# vlyr: layer containing DOC surfaces
		self.vect_doc=self.algo()
		QgsMapLayerRegistry.instance().addMapLayers([self.vect_grd,self.vect_doc,\
		self.vect_map])
		mc.refresh() 
		# mc.setLayerSet(visibility_poly)
		mc.zoomToFullExtent()
		mc.show()

    def saveStation(self,N_st,Lam_st,Fi_st,H_st):
		St=Station(N_st,[Fi_st,Lam_st,H_st])
		St.calculate_visiblilty_conic()
		# print(St.Name, St.Coords)
		self.Regina.add_station(St)
		# print(len(self.Regina.stations))
		self.add_feature2layer(St)
		self.vect_doc=self.algo()
		self.vect_doc.triggerRepaint()

    def add_feature2layer(self, station_added):
		mc=self.iface.mapCanvas()
		n=len(self.Regina.stations)
		pr=self.vect_cover.dataProvider()
		grd_pr=self.vect_grd.dataProvider()
		self.vect_cover.startEditing()
		self.vect_grd.startEditing()
		ptt=station_added.visibility_conic
		# print(station.visibility_conic)
		poly_pt=[]
		# print(len(ptt[0][0]))
		# print(QgsPoint(ptt[0][0][0],ptt[0][1][0]))
		for i in xrange(len(ptt[0][0])):
			poly_pt+=[QgsPoint(ptt[0][0][i],ptt[0][1][i])]
		poly_pt.append(QgsPoint(ptt[0][0][0],ptt[0][1][0]))
		# Instantiate features 
		visib=QgsFeature()
		grd_feat=QgsFeature()
		visib.setGeometry(QgsGeometry.fromPolygon([poly_pt]))
		visib.setAttributes([station_added.Name,n-1])
		# =======================================
		grd_feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(station_added.Coords[1],\
		station_added.Coords[0])))
		grd_feat.setAttributes([station_added.Name])
		# Now add features to providers
		pr.addFeatures([visib])
		grd_pr.addFeatures([grd_feat]) 
		self.vect_cover.setLayerTransparency(80)
		self.vect_cover.updateExtents()
		self.vect_grd.updateExtents()
		self.vect_cover.commitChanges()
		self.vect_grd.commitChanges()
		#=========================================================
		# Labeling the grd network Points
		p = QgsPalLayerSettings()
		p.readFromLayer(self.vect_grd)
		p.enabled = True
		p.fieldName = "grd_name"
		p.placement = QgsPalLayerSettings.OverPoint
		p.displayAll = True
		p.setDataDefinedProperty(QgsPalLayerSettings.Size,\
		True, True, "12", "")
		p.quadOffset = QgsPalLayerSettings.QuadrantBelow
		p.yOffset = 1
		p.labelOffsetInMapUnits = False
		p.writeToLayer(self.vect_grd)
		labelingEngine = QgsPalLabeling()
		mc.mapRenderer().setLabelingEngine(labelingEngine)
		#=========================================================
		# Refresh Layers
		self.vect_cover.triggerRepaint()
		self.vect_grd.triggerRepaint()

    def remove_station(self):
		modified=False
		self.selectTool=SelectTool(self.iface)
		self.iface.mapCanvas().setMapTool(self.selectTool)
		if self.vect_grd.selectedFeatureCount() == 0:
			QMessageBox.information(self.iface.mainWindow(), "Info","There is nothing selected.")
			modified=False
		else:
			modified=True
			msg = []
			msg.append("Selected Feature:")
			for feature in self.vect_grd.selectedFeatures():
				msg.append(" " + feature.attribute("grd_name"))
				QMessageBox.information(self.iface.mainWindow(), "Info", "\n".join(msg))
			self.iface.mapCanvas().unsetMapTool(self.selectTool)
		self.vect_grd.startEditing()
		self.vect_cover.startEditing()
		for feature in self.vect_grd.selectedFeatures():
			self.vect_grd.deleteFeature(feature.id())
			# Update the vector layer self.vect_cover: delete the conic visib
			# of the deleted station
			self.vect_cover.deleteFeature(feature.id())
		if modified:
			reply = QMessageBox.question(self.iface.mainWindow(), "Confirm","Save changes to layer?",\
			QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
			if reply == QMessageBox.Yes:
				self.vect_grd.commitChanges()
				self.vect_cover.commitChanges()
				self.vect_doc=self.algo()
				self.vect_doc.triggerRepaint()
			else:
				self.vect_grd.rollBack()
				self.vect_cover.rollBack()
		else:
			self.vect_grd.rollBack()
			self.vect_cover.rollBack()
	
    def algo(self):
		## delete all features of vectorlayer vlyr before adding the new features
		with edit(self.vect_doc):   
			for feat in self.vect_doc.getFeatures():
				self.vect_doc.deleteFeature(feat.id())
		#=============================================
		provider=self.vect_cover.dataProvider()
		# accessing all features of vectorlayer
		all_features=provider.getFeatures(QgsFeatureRequest())
		# Creating a spatial Index instance
		# index=QgsSpatialIndex()
		all_polygons=[]
		for feature in all_features:
			#index.insertFeature(feature)
			all_polygons.append(QgsGeometry(feature.geometry()))
		# Initialize lists saved_geom: the remaining geometries after an iteration
		# res_level: list containing DOC sorted decreasingly
		saved_geom=[]
		res_level=[]
		# print(all_polygons)
		if (all_polygons[0].overlaps(all_polygons[1])):
			first_int_geom=all_polygons[0].intersection(all_polygons[1])
			saved_geom.append(first_int_geom)
			res_level.append(2)
		first_sd_geom=all_polygons[0].symDifference(all_polygons[1])
		saved_geom.append(first_sd_geom)
		res_level.append(1)
		# print(len(saved_geom))
		for j in xrange(2,4):
			# print(j)
			# print(all_polygons[j])
			levels=[]
			tmp_geom=[]
			# print(saved_geom[1])
			for i in xrange(len(saved_geom)):
				if(all_polygons[j].intersects(saved_geom[i])):
					level=res_level[i]+1
					# print(level)
					New_inter=all_polygons[j].intersection(saved_geom[i])
					# print(New_inter)
					if (New_inter.isGeosValid()):
						levels.append(level)
						tmp_geom.append(New_inter)
					# print(tmp_geom)
					if not (all_polygons[j].contains(saved_geom[i])):
						# There is a rest we need to keep it
						level=res_level[i]
						Rest=saved_geom[i].difference(New_inter)
						# print(Rest)
						if (Rest !=None):
							levels.append(level)
							tmp_geom.append(Rest)
						# print(tmp_geom)
					poly_g=all_polygons[j].difference(New_inter)
					if(poly_g!=None):
						all_polygons[j]=poly_g
					# print(all_polygons[j])
				else:
					level=res_level[i]
					levels.append(level)
					tmp_geom.append(saved_geom[i])
			if not all_polygons[j].isEmpty():
				all_polygons[j].convertToSingleType()
				levels.append(1)
				tmp_geom.append(all_polygons[j])
				"""if(i==len(saved_geom)-1):
					level=1
					rest_of_all=all_polygons[j].symDifference(saved_geom[i])
					levels.append(level)
					tmp_geom.append(rest_of_all)
					"""
			#update saved geometries to new geometries
			saved_geom=[]
			res_level=[]
			# Combine all geometries having the same level
			# print(levels)
			# print(tmp_geom)
			k=0
			while (k<len(levels)):
				nb_occur=levels.count(levels[k])
				if(nb_occur==1):
					saved_geom.append(QgsGeometry(tmp_geom[k]))
					res_level.append(levels[k])
					# print(tmp_geom[k].asMultiPolygon())
				else: 
					tmp=tmp_geom[k].combine(tmp_geom[k+1])
					saved_geom.append(QgsGeometry(tmp))
					res_level.append(levels[k])
					# print("******")
					# print(tmp.asGeometryCollection())
					k+=1
				k+=1
			# print(res_level)
			"""
		# Construct features of all saved_geometries representing different DOCS 
		filename='D:\CHECK_STANDALONE_QGIS_UBUNTU\doc.shp'
		fields=QgsFields()
		writer = QgsVectorFileWriter(filename, "ASCII", fields,
		saved_geom[0].wkbType(),None, "ESRI Shapefile")
		if writer.hasError()!= QgsVectorFileWriter.NoError:
			print "Error!"
			return
			"""
		cc=0
		pr=self.vect_doc.dataProvider()
		pr.addAttributes([QgsField("doc", QVariant.Int)])
		self.vect_doc.startEditing()
		for geometry in saved_geom:
			feature = QgsFeature()
			feature.setGeometry(geometry)
			feature.setAttributes([res_level[cc]])
			self.vect_doc.addFeatures([feature])
			cc+=1
		self.vect_doc.commitChanges()
		# Build renederer categories
		categories=[]
		field='doc'
		features=self.vect_doc.getFeatures()
		cc=0
		for feat in features:
			doc=feat[field]
			fill = QgsSymbolV2.defaultSymbol(self.vect_doc.geometryType())
			fill.setColor(QColor(180,80*cc,60*cc,255))
			category = QgsRendererCategoryV2(doc, fill, r'doc_''%i'%res_level[cc])
			categories.append(category)
			cc+=1
			
		# Color features acoording to field named doc 
		renderer = QgsCategorizedSymbolRendererV2(field, categories)
		self.vect_doc.setRendererV2(renderer)
		self.vect_doc.setLayerTransparency(60)
		return self.vect_doc
		"""
		# face.addVectorLayer('D:\CHECK_STANDALONE_QGIS_UBUNTU\doc.shp','doc','ogr')
		res=prc.runandload('qgis:intersection',layers[1],layers[0],'Inter')
		# res=result['OUTPUT']
		
		# Check intersection result:
		if(res!=0):
			Vects.append(res)
		res=prc.runandload('qgis:symmetricaldifference',layers[1],layers[0],'SD')
		# res=result['OUTPUT']
		Vects.append(res)
		# print("*****, ", Vects)
		for i in xrange(2,len(layers)-29):
			tmp=[]
			j=0
			while (j<len(Vects)):
				flag=prc.runalg('qgis:intersection',Vects[j],layers[i],r'Int_''%i'%(i+1-j))
				# check for intersection result
				# If there is no intersection, wait for the following iteration,if there is an intersection, 
				# one should specify a union operation between two polygons
				if(flag==0):
					j+=1
					flag=prc.runalg('qgis:intersection',Vects[j],layers[i],'Intermediate')
					if (flag==1):
						prc.runalg('qgis:union',"r'Int_''%i'%(i+1-j).shp","Intermediate.shp","r'Int_''%i'%(i+1-j).shp")
						tmp.append("r'Int_''%i'%(i+1-j).shp")
				else:
					tmp.append("r'Int_''%i'%(i+1-j).shp")
				j+=1				
			prc.runalg('qgis:symmetricaldifference',Vects[-1],layers[i],"r'DS_''%i'%(i+1).shp")
			tmp.append("r'DS_''%i'%(i+1).shp")
			Vects=tmp
			# prc.runalg('qgis:union',)			
			"""
