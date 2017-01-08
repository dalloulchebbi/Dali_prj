# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import matplotlib.pylab as plt

#==============================================================
# Fonction qui transforme les coordonnées sur le plan orbital
# en coordionnées ECEF

class transform():
    def transform2ecef(self,x,y,lam,inclinaison,w):
        n1=x*np.cos(w)-y*np.sin(w)
        n2=x*np.sin(w)+y*np.cos(w)
        X= n1*np.cos(lam)-n2*np.sin(lam)*np.cos(inclinaison)
        Y= n1*np.sin(lam)+n2*np.cos(lam)*np.cos(inclinaison)
        Z= n2*np.sin(inclinaison)
        return X,Y,Z
    def transform2geog(self,x,y,z,exc,f,a):
        R=np.sqrt(x**2+y**2+z**2)
        lambda_geo=self.arctan_def(y,x)
        mu=np.arctan((z/(np.sqrt(x**2+y**2)))*((1-f)+((exc**2)*a/R)))
        phi=np.arctan((z*(1-f)+(exc**2)*a*np.sin(mu)**3)/((1-f)*(np.sqrt(x**2+y**2)-(exc**2)*a*np.cos(mu)**3)))
        h=(np.sqrt(x**2+y**2)*np.cos(phi))+(z*np.sin(phi))-(a*np.sqrt(1-(exc**2)*np.sin(phi)**2))
        return lambda_geo,phi,h
    def compute_Latiso(self,Phi, exc):
        latiso = np.log(np.tan(np.pi/4+Phi/2))-(exc/2)*np.log((1+exc*np.sin(Phi))/(1-exc*np.sin(Phi)))
        return latiso
    def transform2geocentric(self,lam,fi,e1terre,grand_axe):
        ww=np.sqrt(1-e1terre**2*np.sin(fi)**2)
        N=grand_axe/ww
        X_terre=N*np.cos(fi)*np.cos(lam)
        Y_terre=N*np.cos(fi)*np.sin(lam)
        Z_terre=N*(1-e1terre**2)*np.sin(fi)
        return X_terre,Y_terre,Z_terre
    def arctan_def(self,a,b):
		res=0
		if (a>0 and b> 0):
			res = np.arctan(a/b)
		elif (a >= 0 and b<0):
			res = np.pi+np.arctan(a/b)
		elif (a<0 and b<0):
			res = np.arctan(a/b)-np.pi
		elif (a<0 and b> 0):
			res=np.arctan(a/b)
		elif (a > 0 and b==0):
			res = np.pi/2
		elif (a < 0 and b==0):
			res = -np.pi/2
		else:
			print("function not defined")
		return res
#===========================================================
