# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import matplotlib.pylab as plt
import Transform2
import Transform

def transform_deg_2rad(angle):
    rad_angle =(angle*np.pi)/180.0
    return rad_angle
#==========================================================
# Paramètres de l'ellipsoîde IAG GRS 80 ASSOCIÉ AU RGF93
f = 1/298.257223563
e1_terrestre = np.sqrt(2*f-f**2)
a_terrestre = 6378137.0
# =========================================================
# Paramètres de la projection Mercator
# =========================================================
xc = 0.0
yc =0.0
n = 6378137.0
#==========================================================
teta = 80.0*np.pi / 180.0
hauteur = 23000000.0
"""
 DANS CE QUI SUIT, ON ADOPTE UNE SEULE HAUTEUR CONVENTIONNELLE
 DE VOL POUR CHAQUE CONSTELLATION. ON PROJETTE LES CÖNES SUR LA 
 BASE DE CETTE HAUTEUR 
 """
class Station():
	def __init__(self,Name,Coords):
		self.Name=Name
		self.Coords=Coords
		self.visibility_conic=[]
		
	def calculate_visiblilty_conic(self):
		# test de la projection d'un cône sur la surface terrestre
		beta = np.linspace(0,2*np.pi,400,True)
		lambda_station=transform_deg_2rad(self.Coords[1])
		pfi_station=transform_deg_2rad(self.Coords[0])
		ww=np.sqrt(1-(e1_terrestre**2)*np.sin(pfi_station)**2)

		matrix = np.array([[np.sin(pfi_station)*np.cos(lambda_station),-np.cos(pfi_station)*np.sin(lambda_station),0], \
				[np.sin(pfi_station)*np.sin(lambda_station),np.cos(pfi_station)*np.cos(lambda_station),0], \
				 [-np.cos(pfi_station),0,0]])
		vect=np.array([np.cos(beta),np.sin(beta),0]).T
		N1=a_terrestre/ww
		O_station=np.array([(N1+hauteur)*np.cos(pfi_station)*np.cos(lambda_station),\
							  (N1+hauteur)*np.sin(lambda_station)*np.cos(pfi_station),\
							  (N1*(1-e1_terrestre**2)+hauteur)*np.sin(pfi_station)]).T
		XYZ_cone=O_station+hauteur*np.tan(teta)*np.dot(matrix,vect)
		x_cone=XYZ_cone[0]
		y_cone=XYZ_cone[1]
		z_cone=XYZ_cone[2]
		trans_cone=Transform2.transform()
		lam_cone,fi_cone=trans_cone.transform2geog(x_cone,y_cone,z_cone,e1_terrestre,f,a_terrestre)
		lam_cone_adjusted,fi_cone_adjusted=self.close_opened_areas(lambda_station,pfi_station,lam_cone,fi_cone)
		self.visibility_conic.append([lam_cone_adjusted,fi_cone_adjusted])
		# self.stations_coordinates.append([E_station,N_station])		
		
	def close_opened_areas(self,lam_station,fi_station,lam_coord,fi_coord):
		fi_min=-88.0*np.pi/180.0
		fi_max=88.0*np.pi/180.0
		lam_max=np.pi
		lam_min_allowed=-lam_max
		lam_max_allowed=lam_max
		# tr=Transform.transform()
		# latiso_min=tr.compute_Latiso(fi_min,e1_terrestre)
		# latiso_max=tr.compute_Latiso(fi_max,e1_terrestre)
		# y_min=yc+n*latiso_min
		# y_max=yc+n*latiso_max		
		#Delete out-of-bound values max_values
		ofb_val_fi_max=np.argwhere(fi_coord>fi_max)
		for i in xrange(len(ofb_val_fi_max)):
			fi_coord[ofb_val_fi_max[i]]=fi_max
		#Delete out-of-bound values min_values
		ofb_val_fi_min=np.argwhere(fi_coord<fi_min)
		for i in xrange(len(ofb_val_fi_min)):
			fi_coord[ofb_val_fi_min[i]]=fi_min	
		#Recherche de la distance par rapport au milieu des abscisses
		# _mil=lam_coord-xc
		# Détermination des abscisses les plus proches du milieu de part et d'autre
		lam_right_middle=min([i for i in lam_coord if i>0])
		lam_left_middle=max([i for i in lam_coord if i<0])
		if(((lam_right_middle-lam_left_middle)/(2*lam_max))>0.4):
			for i in xrange(len(lam_coord)):
				if (lam_coord[i]<0):
					lam_coord[i]+=2*lam_max_allowed	
		# lam_coord=lam_coord.tolist()
		fi_coord=fi_coord.tolist()
		lam_min=min(lam_coord)
		lam_max=max(lam_coord)
		pos_min=lam_coord.index(lam_min)
		pos_max=lam_coord.index(lam_max)
		pos_ficmin=fi_coord.index(min(fi_coord))
		pos_ficmax=fi_coord.index(max(fi_coord))
		lam_ficmin=lam_coord[pos_ficmin]
		lam_ficmax=lam_coord[pos_ficmax]
		
		if(((np.abs(lam_max-lam_min)/(2*lam_max))>0.8)):
			if(np.abs(lam_ficmin-lam_station)>np.abs(lam_ficmax-lam_station)):
				lam_coord.insert(pos_min+1,lam_min)
				lam_coord.insert(pos_max+1,lam_max)
				fi_coord.insert(pos_min+1,fi_min)
				fi_coord.insert(pos_max+1,fi_min)
			else:
				lam_coord.insert(pos_min,lam_min)
				lam_coord.insert(pos_max+1,lam_max)
				fi_coord.insert(pos_min,fi_max)
				fi_coord.insert(pos_max+1,fi_max)
			# print("Undone Staff")
			lam_coord=np.asarray(lam_coord)*180.0/np.pi
			fi_coord=np.asarray(fi_coord)*180.0/np.pi
		return lam_coord,fi_coord	
			
class Ground_network():
	def __init__(self):
		self.stations=[]
	#========================================================================================================
	"""Ajout d'une station au réseau"""
	#========================================================================================================
	def add_station(self,t):
		self.stations.append(t)
	#=========================================================================================================
	"""	Elimination d'une station"""
	#=========================================================================================================
	def del_station(self,t):
		self.stations.remove(t)
	#=========================================================================================================	
	#=========================================================================================================
	"""	Ajout d'une liste de stations"""
	#=========================================================================================================
	def add_stations(self,list_stations):
		for t in list_stations:
			self.stations.append(t)