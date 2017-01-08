# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import Transform

meth_atan2=Transform.transform()

# ==========================================================#
#  L'objet de type Orbit_anomaly possède les méthodes qui   #
#  permettent de:                                           #
#                                                           #
# 1.calcluer l'anomalie moyenne à un instant t quelconque   #
# 2.calculer l'anomalie excentrique moyenne                 #
# 3.Détreminer le rayon orbital à chaque instant t          #
# ==========================================================#
class Orbit_anomaly():
    def __init__(self):
        self.anomalie_t=[]
	#=======================================================
    """Calcul de l'anomalie à l'nstant de calcul des positions""" 
	#=======================================================
    def get_anomalie(self,meananom,pulsation,time_tle,time):
        M_t=meananom+pulsation*(time-time_tle)
        self.anomalie_t.append(M_t)
	#=======================================================
	
	#=======================================================
    """Calcul de l'anomalie excentrique"""
	#=======================================================	
    def get_anomalie_excentrique(self,e1):
        E0=self.anomalie_t
        E=[]
        excentr_moins=E0
        erreur=1e-10
        for i in xrange(2000):
            excentr_plus=E0+e1*np.sin(excentr_moins)
            if(np.all(np.abs(excentr_plus-excentr_moins)<=erreur)):
                break
            excentr_moins = excentr_plus
        Anomalie_execentrique=excentr_plus
        return Anomalie_execentrique
	#=======================================================
	
	#=======================================================
    """Calcul du rayon orbital"""
	#=======================================================	
    def get_rayon_orbital(self,a,e1,e_t):
        rayon=a*(1-e1*np.cos(e_t))
        return rayon
	#=======================================================
	
	#=======================================================
    """Calcul de l'anomalie vraie """
	#=======================================================		
    def cal_anomalie_vraie(self,e1,e_t):
        terme1=np.sqrt(1-e1**2)*np.sin(e_t)
        terme2=np.cos(e_t)-e1
        v=meth_atan2.arctan_def(terme1,terme2)
		# j'ai migré vers scalaires terme1 au lieu de terme1[i]
        return v
	#=======================================================
	
	#=======================================================
    """Calcul du temps de passaage du Noeud ascendant à la 
    position actuelle"""
	#=======================================================
    def get_delta_t(self,e1,w,Meananomaly,pulse):
        y = np.sqrt(1-e1)*np.tan(-w)
        x = np.sqrt(1+e1)
        Anomalie_excen=2*np.arctan(y/(x+np.sqrt(x** 2+y**2)))
        Mean_anomaly_Na =Anomalie_excen-e1*np.sin(Anomalie_excen)
        deltaM = Meananomaly-Mean_anomaly_Na
        #periode = 2*pi/pulse
        #print("periode:",periode)
		
		# pour avoir un temps il faut diviser des angles par des vitesses angulaires et pas des périodes
        delta_t = deltaM/pulse 
        return delta_t
	#=======================================================
	
	#=======================================================
    """Calcul de la longitude au noeud ascendant"""
	#=======================================================		
    def get_lambda_na(self,omega,gmst,omegapoint,deltatime):
        lambda_na=omega-(gmst+omegapoint*deltatime)
        return lambda_na
	# ======================================================
