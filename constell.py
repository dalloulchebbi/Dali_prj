# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
from pylab import *
import math as mm
import matplotlib.pylab as plt
import time
#==========================================================
import Orbit_anomaly
import GPSTIME as gpst
import Transform
#==========================================================
"""Paramètres de l'ellipsoîde IAG GRS 80 ASSOCIÉ AU RGF93"""
f = 1.0/298.257223563
e1_terrestre = np.sqrt(2*f-f**2)
a_terrestre = 6378137.0
# =========================================================
"""Vitesse angulaire de rotation terrestre en rad/s"""
omegapoint = -7.2921151467e-5
# =========================================================
xc = 0.0
yc = 0.0
n = 6378137.0

k=3.986004418e14
rayon=6378137.0

# =========================================================
"""TRANSFORMATION DE DEGRéS en Radians"""
def transform_deg_2rad(angle):
    rad_angle =(angle*np.pi)/180.0
    return rad_angle
# =========================================================

"""get actual time for updating measures"""
tt = time.gmtime()
"""Calculate Julian Time in seconds"""
actual_time=(tt.tm_year%2000)*365.25*86400.0+tt.tm_yday*86400.0+tt.tm_hour*3600.0+tt.tm_min*60.0+tt.tm_sec

#=======================================================================================================#
#              Définition  de la class Constellation  définie par son nom,qui                           #
#              contient les satellites et la liste de tous les tle associés                             #
#               Chaque TLE: Relatif à chaque satellite qui lui, est  défini                             #
#                                       par son nom                                                     #
#=======================================================================================================#
class Constellation():
    def __init__(self,name):
        self.name=name
        self.list_TLE_by_sat=[]
        self.actual_geog_position=[]
        self.actual_projection_position=[]
        self.pulsation_satellite=[]
        self.demi_gaxe_sat=[]
        self.actual_geocentric_position=[]
    def retrieve_data_from_filename(self,file_name):
        file = open(file_name)
        lines = file.readlines()
        file.close()
        for i in xrange(long(len(lines) / 3)):
            Name_sat = lines[3*i]
            ligne1 = lines[1 + 3*i]
            yy = long(ligne1[18:20])
            dd = float(ligne1[20:32])
            ligne2 = lines[2+3*i]
            revolutionperday = float(ligne2[52:63])
            inclination = transform_deg_2rad(float(ligne2[8:16]))
            omega = transform_deg_2rad(float(ligne2[17:25]))
            # in degrees need to transform to radians
            e1_satellite = float(ligne2[26:33])*1e-7  # excentricity
            w = transform_deg_2rad(float(ligne2[34:42]))
            # in degrees need to transform to radians
            Meananomaly = transform_deg_2rad(float(ligne2[43:51]))
            # in degrees need to transform to radians
            # annee_decimale.append(yy+dd/365)
            """
            print("check data")
            print(Name_sat)
            print(yy)
            print(dd)
            print(revolutionperday)
            print("inclinaison",float(ligne2[8:16]))
            print("omega",float(ligne2[17:25]))
            print("excentricte",e1_satellite)
            print("perigee",float(ligne2[34:42]))
            print("anomalie moyenne",float(ligne2[43:51]))
            """
            tle_sat = TLE(yy, dd, revolutionperday, inclination, omega, e1_satellite,w,Meananomaly)
            self.pulsation_satellite.append(tle_sat.determine_grand_axe_and_pulsation()[1])
            self.demi_gaxe_sat.append(tle_sat.determine_grand_axe_and_pulsation()[0])
            self.list_TLE_by_sat.append(tle_sat)
    def get_constellation_position(self):
        # =====================================================================================#
        #           Recherche des coordonnées des satellites dans le repère                    #
        #           ECEF: EARTH CENTERED EARTH FIXED                                           #
        #           Obtient cette position à partir des éléments Képleriens issus              #
        #           des fichiers TLE Norad                                                     #
        # =====================================================================================#
        #           Cette position est précise à quelques centaines de mètres Près             #
        #           Elle sera utile dans le suivi des constellations sur des plages            #
        #           temporelles entrées par l'utlisateur                                       #
        ##=====================================================================================#
        for i in xrange(len(self.demi_gaxe_sat)):
            Year = self.list_TLE_by_sat[i].year
            Julianday = self.list_TLE_by_sat[i].day
            Excentricite = self.list_TLE_by_sat[i].e1_satellite
            inclinaison = self.list_TLE_by_sat[i].incline
            OMEGA = self.list_TLE_by_sat[i].omega
            W = self.list_TLE_by_sat[i].w
            M = self.list_TLE_by_sat[i].Meananomaly
            # ===================================================================================
            """passage en secondes, temps de référence"""
            # ===================================================================================
            temps_tle=(Year*(365.25)+Julianday)*24*3600  
            # ===================================================================================
            anomalie_sat = Orbit_anomaly.Orbit_anomaly()
            GMST_TLE = gpst.gpstime()
            dtime = anomalie_sat.get_delta_t(Excentricite, W, M, self.pulsation_satellite[i])
            time_Na = temps_tle-dtime
            
            # ===================================================================================
            """Il faut savoir entrer la julian date séparemment"""
            GMST_TLE.yyyyddds_t(Year+2000.0,long(Julianday),(Julianday-long(Julianday))*86400.0)
            # ===================================================================================
            
            gmst = GMST_TLE.GMST*15.0*np.pi/180.0
            lambda_noeud_ascendant = anomalie_sat.get_lambda_na(OMEGA,gmst,omegapoint,dtime)
            anomalie_sat.get_anomalie(M, self.pulsation_satellite[i],temps_tle,actual_time)
            E_t = anomalie_sat.get_anomalie_excentrique(Excentricite)
            Rayon_t=anomalie_sat.get_rayon_orbital(self.demi_gaxe_sat[i],Excentricite, E_t)
            Anomalievraie=anomalie_sat.cal_anomalie_vraie(Excentricite, E_t)

            # ===================================================================================
            """Calcul des coordonnées dans le plan orbital ainsi que la longitude instantannée
            pour le transfert entre systèmes de coordonnées"""
            # ===================================================================================
            
            x_orbite = Rayon_t*np.cos(Anomalievraie)
            y_orbite = Rayon_t*np.sin(Anomalievraie)
            lambda2ecef=lambda_noeud_ascendant+(actual_time-time_Na)*omegapoint
            transformecef=Transform.transform()
            X_ecef,Y_ecef,Z_ecef=transformecef.transform2ecef(x_orbite,y_orbite,lambda2ecef,inclinaison,W)
            self.actual_geocentric_position.append([X_ecef,Y_ecef,Z_ecef])
            Lambda_satellite,phi_satellite,h_satellite=transformecef.transform2geog(X_ecef,Y_ecef,Z_ecef,e1_terrestre,f,a_terrestre)
            self.actual_geog_position.append([Lambda_satellite,phi_satellite,h_satellite])
            latitude_isometrique_satellite = transformecef.compute_Latiso(phi_satellite, e1_terrestre)
            x_satellite = xc+ n*np.asarray(Lambda_satellite)
            y_satellite = yc+n*np.asarray(latitude_isometrique_satellite)
            self.actual_projection_position.append([x_satellite, y_satellite])
#==================================================================================================
"""Définition  de la class Satellite qui contient les TLE
Relatifs à chaque satellite qui lui, est  défini par son nom"""
#==================================================================================================

class satellite():
    def __init__(self,name):
        self.name=name
        self.tle=[]
    def affiche(self):
        for p in self.tle:
            p.affiche()
    def get_tle(self):
        out_tle=self.tle
        return out_tle
    def add_tle(self,t):
        self.tle.append(t)
        
#=================================================================================================
"""Définition de la classe TLE qui permet de lire les données
issues d'un fichier norad et permet de les extraire"""
#=================================================================================================
class TLE():
    def __init__(self,year=0,day=0.0, revolution_number=0.0,incline=0.0,omega=0.0,e1_satellite=0.0,\
                 w=0.0,Meananomaly=0.0):
        self.year=year
        self.day=day
        self.revolution_number=revolution_number
        self.incline=incline
        self.omega=omega
        self.e1_satellite=e1_satellite
        self.w=w
        self.Meananomaly=Meananomaly
    def determine_grand_axe_and_pulsation(self):
        rev_per_day=self.revolution_number # révolutions par jour
        pulsation = rev_per_day*2*np.pi/(24*3600)
        a=(k/pulsation**2)**(1/3)
        return a,pulsation
    def calAlt(self):
        return self.determine_grand_axe_and_pulsation()[0]-rayon
    def affiche(self):
        print(self.year,self.day,self.revolution_number,self.i,self.omega,\
              self.w,self.e1_satellite,self.Meananomaly)
#=================================================================================================
# **************THE END===THE END====THE END===THE END===THE END**********************************
#=================================================================================================
