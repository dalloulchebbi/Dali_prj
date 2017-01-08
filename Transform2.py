# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pylab as plt
#==============================================================
# Fonction qui transforme les coordonnées sur le plan orbital
# en coordionnées ECEF

class transform():
    def __init__(self):
        self.l=[]
    def transform2ecef(self,x,y,lam,inclinaison,w):
        X=[]
        Y=[]
        Z=[]
        for i in range(size(x)):
            mat_rot_lambda=np.array([[np.cos(lam[i]),-np.sin(lam[i]),0],[np.sin(lam[i]),np.cos(lam[i]),0],[0,0,1]])
            mat_rot_i=np.array([[1,0,0],[0,np.cos(inclinaison),-np.sin(inclinaison)],[0,np.sin(inclinaison),np.cos(inclinaison)]])
            mat_rot_w=np.array([[np.cos(w),-np.sin(w),0],[np.sin(w),np.cos(w),0],[0,0,1]])
            xyzecef=np.dot(mat_rot_lambda,np.dot(mat_rot_i,(np.dot(mat_rot_w,np.asarray([x[0][i],y[0][i],0])))))
            X.append(xyzecef[0])
            Y.append(xyzecef[1])
            Z.append(xyzecef[2])
        return X,Y,Z
    def transform2geog(self,x,y,z,exc,f,a):
        R=np.sqrt(np.asarray(x)**2+np.asarray(y)**2+np.asarray(z)**2)
        lambda_geo=self.atan2(y,x)
        #lambda_geo=np.asarray(lambda_geo)
        mu=np.arctan((np.asarray(z)/(np.sqrt(np.asarray(x)**2+np.asarray(y)**2)))*(1-f+(exc**2)*a/R))
        phi=np.arctan((np.asarray(z)*(1-f)+(exc**2)*a*np.sin(mu)**3)/((1-f)*(np.sqrt(np.asarray(x)**2+np.asarray(y)**2)-(exc**2)*a*np.cos(mu)**3)))
        # seulement pour le traçage de cône
        # on aura besoin de changer les valeurs des lattitudes
        # il faur ramener les zones qui débordent à la vue cartographique
        """
        if (lambda_station >=0 and lambda_station < np.pi):
            for i in range(len(y)):
                if (y[i]<0):
                    lambda_geo[i]+=np.pi"""
        return lambda_geo,phi
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
    def atan2(self,a, b):
        tab_lam = []
        for i in range(len(a)):
            if (b[i] > 0):
                res = np.arctan(a[i]/b[i])
            elif (a[i] >= 0 and b[i]<0):
                res = np.arctan(a[i]/b[i])+np.pi
            elif (a[i] < 0 and b[i]<0):
                res = np.arctan(a[i]/b[i])-np.pi
            elif (a[i] > 0 and b[i]==0):
                res = np.pi / 2
            elif (a[i] < 0 and b[i]==0):
                res = -np.pi / 2
            else:
                print("undefined atan2")
            tab_lam.append(res)
        return tab_lam

#===========================================================

