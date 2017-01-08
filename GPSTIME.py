# -*- coding: iso-8859-15 -*-
"""
GPS time/date management
Beilin Jacques 
ENSG/IGN

2015-08-05 JBL
    1. utilisation du module decimal pour gerer les multiplications grands nombre / grande precision
2015-10-02 JBL 
    1. utilisation du module Decimal dans add_s, add_h et add_day
2015-12-26 JBL
    1. creation d'un getter/setter pour wsec pour gerer le passage decimal/float
2016-06-14 1.0.14 JBL
    1. ajout d'une sortie au format pyephem pour les calcul d'azimut par le soleil  
2016-06-15 1.0.15 JBL
    1. gestion de l'affichage de l'aide
2016-06-27 1.0.16 JBL
    1. ajouts des fonctions snx_t et st_snx_epoch : entrée/sortie en date sinex
2016-06-28 1.0.17 JBL
    1. ajout de return à toutes les fonctions xx00 et add_x pour pouvoir les enchainer

"""
 
import re
import time as tm
import math
import os
import decimal
import numpy as np

class gpstime():
    """GPS time management
    Jacques Beilin - ENSG/DPTS - 2016-06-27
    
    """
    version = "2016-06-27"
         
    # constant definitions
    _DAY = ['SUN','MON','TUE','WED','THU','FRI','SAT']
    _MON = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    _SESSION = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','0']
    _GPS0 = 315964800.0  # 1980-01-06 in seconds starting from 1970-01-01T00:00:00
    _MJD2000 = 51544.5   # J2000 en mjd
    _J2000 = 946728000.0 # J2000 en secondes a partir de 1970-01-01
    _J1950 = 2433282.50  # constante de calcul des jours juliens 1950 
    _JD2000 = 2451545.0  # J2000 in jd
    
    def __init__(self):        
        self.just_now() # par defaut on initialise à l'heure système
    
    # Exemple de getter et de setter, assez contre-productif dans cet exemple    
    # etant donne que le setter ne met pas à jour les autres champs de la classe
    @property
    def mjd(self):
        return self._mjd
    @mjd.setter
    def mjd(self,ModifiedJulianDate):
        self._mjd = ModifiedJulianDate
    
    # getter/setter indispensable pour assurer la conversion float/decimal    
    @property
    def wsec(self):
        return float(self._wsec)
    @wsec.setter
    def wsec(self,SecondOfWeek):
        self._wsec = SecondOfWeek
        
    def _s1970_t(self,s1970=0):
        """Calculate all time elements from seconds starting from 1970-01-01T00:00:00

        **Input** :
          : s1970 : number of seconds  from 1970-01-01T00:00:00

        **Output** :
          : self : updated gpstime object

	:Example:

	t._s1970_t(260054524.0)

	"""        
        self.s1970 = s1970 # secondes a partir de 1970-01-01
        #print("s1970 = ",s1970)
        T = tm.gmtime(s1970)
        a = decimal.Decimal(s1970)
        
        #problème de compilation python 2.7 entre type decimal et float
        # donc ajout de a_entiere qui permet de donner la partie entiere
        a_entiere=decimal.Decimal(math.floor(a))
        _decimal_sec = decimal.Decimal(a-a_entiere)

        self.mjd = (float(s1970) - gpstime._J2000) / 86400 + gpstime._MJD2000
        self.jd = self.mjd + 2400000.5 # jour julien
        self.jd50 = self.jd - gpstime._J1950 # JD 1950 (GRGS)
        
        _frac_of_day = decimal.Decimal(T.tm_hour * 3600.0) + decimal.Decimal(T.tm_min * 60.0) + decimal.Decimal(T.tm_sec) + _decimal_sec    
        self.dsec = float(_frac_of_day) # secondes du jour
        
        _dsecg = decimal.Decimal(s1970) - decimal.Decimal(gpstime._GPS0) # secondes depuis GPS0
        njgps = math.floor ( float(_dsecg / decimal.Decimal(86400.0)) ) # jours entiers depuis GPS0
        self.wk = math.floor ( njgps / 7) # semaine GPS
        self.wsec = _dsecg - decimal.Decimal(self.wk *7*86400.0) # seconde dans la semaine 
        
        #print("_dsecg = ",_dsecg)
        
        self.yyyy = T.tm_year # annee 
        if self.yyyy < 2000:
            self.yy = self.yyyy - 1900;
        else:
            self.yy = self.yyyy - 2000;
            
        self.mon = T.tm_mon # mois
        self.mm_en = gpstime._MON[int(round(self.mon-1))]
        self.dd = T.tm_mday # jour dans le mois

        self.hh = T.tm_hour # heure
        self.ses = gpstime._SESSION[int(round(self.hh))] # session
        self.min = T.tm_min # minute
        self.sec = T.tm_sec + (self.dsec - math.floor(self.dsec)) 

        self.doy = T.tm_yday # jour de l'annee 
        self.wd = math.fmod(T.tm_wday + 1,7)  # jour de la semaine (dimanche->0)
        self.wd_en = gpstime._DAY[int(round(self.wd))]

        self.dy = self.yyyy + (self.doy - 1  + self.dsec / 86400.0) / 365.25 # decimal year

        #    Computing GMST
        D = self.jd - 2451545.0 # Julian days since J2000
        T = D / 36525.0 # Julian centuries since J2000
        GMST =  18.697374558 + 24.06570982441908 * (self.jd - 2451545.0);
        self.GMST = math.fmod(GMST,24.0) # Unit : decimal hour
        if self.GMST<0:
            self.GMST+=24.0

        # Computing Equation of Equinoxes
        d2r = math.pi / 180.0
        Omega = 125.04 - 0.052954 * D # Longitude of the ascending node of the Moon
        L = 280.47 + 0.98565 * D # Mean Longitude of the Sun
        epsilon = 23.4393 - 0.0000004 * D # obliquity
        Delta_psi = -0.000319 * math.sin (Omega*d2r) - 0.000024 * math.sin (2*L*d2r) # nutation in longitude
        self.EQEQ = Delta_psi * math.cos(epsilon * d2r);

        # Computing GMST
        self.GAST = self.GMST + self.EQEQ;    
        if self.GAST<0:
            self.GAST+=24.0

        
    def just_now(self):
        """Calculates all time elements current computer time
        
        Output :
        - self : updated gpstime object
        """
        s1970 = tm.time()# seconds starting from 1970-01-01T00:00:00
        self._s1970_t(s1970)
        
    def ymdhms_t(self,y=1980,m=1,d=6,hh=0,mm=0,ss=0):
        """Calculate all time elements from year, DOY and as an option seconds of day
        Input :
          y, m, d : year, month, day
          hh, mm, ss : hour, minute, second
        
        User can also provide a 1 to 6 (y,m,d,h,m,s) elements list
        all elements in list are ordered.
        Default values taken from (1980,01,06,0,0,0)
        
        Output :
          self : updated gpstime object"""
                    
        if isinstance(y,list):
            if len(y)>5:
                ss=int(y[5])
            if len(y)>4:
                mm=int(y[4])
            if len(y)>3:
                hh=int(y[3])
            if len(y)>2:
                d=int(y[2])
            if len(y)>1:    
                m=int(y[1])
            if len(y)>0:
                y=float(y[0])
                        
        else:
            y=int(y)
            m=int(m)
            d=int(d)
            hh=int(hh)
            mm=int(mm)
            ss=float(ss)
            
        #2 or 4 digits year management
        if y<80:
            y=y+2000
        elif y<100:
            y=y+1900
        os.environ['TZ'] = 'GMT'
        
        t= (y, m, d, hh, mm, int(ss), 0, 0, 0)#, tm_wday=3, tm_yday=335, tm_isdst=-1)
        s1970 = decimal.Decimal(tm.mktime(t))  
        frac_sec = decimal.Decimal(ss - int(ss))
        s1970 = s1970 + frac_sec

        self._s1970_t(s1970);

    def yyyyddds_t(self,yyyy,ddd,s=0.0):
        """Calculate all time elements from year, DOY and as an option seconds of day
        Input :
          yyyy : year
          ddd : DOY
          s : second of day [0-86400] [default value =0])
        
        Output :
          self : updated gpstime object
          
        """
        self.ymdhms_t(yyyy,1,1,0,0,0);
        self.add_s((ddd-1.0)*86400.0+s)
                    
    def gpswkd_t(self,gpsweek, wday=0.0):
        """Calculate all time elements from GPS week and day of week
        Input :
          yyyy : year
          gpsweek : GPS week
          wday : Day of week (sunday = 0 [default value])
        
        Output :
          self : updated gpstime object

        """
        njgps = gpsweek * 7.0 + wday
        s1970 = njgps * 86400.0 + gpstime._GPS0
        self._s1970_t(s1970)
        
    def gpswks_t(self,gpsweek, wsec=0.0):
        """Calculate all time elements from year, DOY and as an option seconds of day
        Input :
          yyyy : year
          ddd : DOY
          s : second of day [0-86400] [default value 0]
        
        Output :
          self : updated gpstime object
          
        """
        s1970 = gpsweek * 7 * 86400 + wsec + gpstime._GPS0
        self._s1970_t(s1970)
        
    def dy_t(self,decimal_year):
        """Calculate all time elements from year, DOY and as an option seconds of day
        Input :
          decimal_year : decimal year (float)
        
        Output :
          self : updated gpstime object
          
        """
        yyyy = math.floor(decimal_year)
        doyd = 1 + (decimal_year-yyyy)*365.25
        doy  = math.floor(doyd)
        sec = (doyd - doy) * 86400.0
        self.yyyyddds_t(yyyy,doy,sec);
            
    def mjd_t(self,mjd=0):
        """Calculate all time elements from Modified Julian Date
        Input :
          mjd : Modified Julian Date (float)
        
        Output :
          self : updated gpstime object
        """
        s1970 = (mjd - gpstime._MJD2000) * 86400 + gpstime._J2000 # seconds starting from 1970-01-01T00:00:00
        self._s1970_t(s1970)
        
    def jd_t(self,julian_date=0):
        """Calculate all time elements from Julian Date
        Input :
          julian_date : Julian Date (float)
        
        Output :
          self : updated gpstime object
        """
        s1970 = (julian_date - gpstime._JD2000) * 86400.0 + gpstime._J2000 # seconds starting from 1970-01-01T00:00:00
        self._s1970_t(s1970);
        
    def jd50_t(self,julian_date_50=0):        
        """Calculate all time elements from Julian Date 1950 (GRGS)
        Input :
          julian_date_50 : Julian Date 1950 (float)
        
        Output :
          self : updated gpstime object
        """
        s1970 = (julian_date_50 - 7305) * 86400# seconds starting from 1970-01-01T00:00:00
        self._s1970_t(s1970)    
        
    def snx_t(self,st_snx):
        """Calculate all time elements from Sinex time string
        Input :
          st_snx : SINEX time string (yy:doy:sssss string)
        
        Output :
          self : updated gpstime object
        """
        
        tab_snx=st_snx.split(":")
        
        yy = float(tab_snx[0])
        doy = float(tab_snx[1])        
        dsec = float(tab_snx[2])        
     
        self.yyyyddds_t(yy,doy,dsec)    
        
    def iso_t(self,st_iso):
        """Calculate all time elements from ISO time string
        Input :
          st_iso : ISO time string (yyyy-mm-ddThh:mm:ss.sss string)
        
        Output :
          self : updated gpstime object
        """
        st_iso = re.sub("Z$","",st_iso) # on vire la lettre Z en fin de chaine
        st_iso = re.sub(":","-",st_iso)
        st_iso = re.sub("T","-",st_iso)
        tab_iso=st_iso.split("-")
        
        yyyy = float(tab_iso[0])
        mm = float(tab_iso[1])        
        dd = float(tab_iso[2])        
        h = float(tab_iso[3])        
        m = float(tab_iso[4])
        s = float(tab_iso[5])        

        self.ymdhms_t(yyyy,mm,dd,h,m,s)    
        
    def rinex_t(self,rinex_time_str):
        """Calculate all time elements from RINEX time string
        Input :
          rinex_time_str : RINEX time string
        
        Output :
          self : updated gpstime object
          
        """
        list_strdate=rinex_time_str.split()
        self.ymdhms_t(float(list_strdate[0]),float(list_strdate[1]),float(list_strdate[2]),float(list_strdate[3]),float(list_strdate[4]),float(list_strdate[5]))
        
    def add_s(self,s=0.0):
        """Add s seconds to a gpstime object
        Input :
          s : number of seconds (+/-)
        
        Output :
          self : updated gpstime object
        """
        self._s1970_t(decimal.Decimal(self.s1970) + decimal.Decimal(s))    
        return self
        
    def add_h(self,h=0.0):
        """Add h hours to a gpstime object
        Input :
          h : number of hours (+/-)
        
        Output :
          self : updated gpstime object
        """
        self._s1970_t(self.s1970 + decimal.Decimal(h * 3600.0))
        return self
        
    def add_day(self,d=0.0):
        """Add d days to a gpstime object
        Input :
          d : number of days (+/-)
        
        Output :
          self : updated gpstime object
        """
        self._s1970_t(self.s1970 + decimal.Decimal(d * 86400.0))
        return self
     
    def wk00(self):
        """Fill a gpstime object with current week on sunday at 00:00:00
        """
        self.gpswkd_t(self.wk, 0.0)
        return self
           
    def day00(self):
        """Fill a gpstime object with current day at 00:00:00
        """
        self.mjd_t(math.floor(self.mjd))
        return self        
        
    def h00(self):
        """Fill a tgps structure with current hour at 00 minuts
        """
        self.ymdhms_t(self.yyyy,self.mon,self.dd,self.hh,0,0)
        return self

    def m00(self):
        """Fill a tgps structure with current minute at 00 seconds
        """
        self.ymdhms_t(self.yyyy,self.mon,self.dd,self.hh,self.min,0)
        return self
            
    def print_dates(self):    
        print("Gpstime (version %s)" % (gpstime.version))
        print("-----------------------------------------------------------------")
        print("s1970 : %.6f" % (self.s1970))
        print("YYYY_MM_DD : %4.0f/%02.0f/%02.0f  \nHH:MM:SS : %02.0f:%02.0f:%012.9f" % (self.yyyy,self.mon,self.dd,self.hh,self.min,self.sec))        
        print("GPS week : %04d\nDay of week : %1d (%s)\nSecond of week : %-16.9f\nSecond of day : %-16.9f \nsession : %s" % (self.wk,self.wd,self.wd_en,self.wsec,self.dsec,self.ses)) 
        print("Modified Julian Date : %.6f  \nJulian Date : %.6f" % (self.mjd, self.jd)) 
        print("YYYY : %04d  DOY : %03d" % (self.yyyy, self.doy))     
        print("GMST (dec. hour) : %.6f" % (self.GMST))
        print("GAST (dec. hour) : %.6f\nEq. of Equinoxes (dec. hour) : %.6f" % (self.GAST,self.EQEQ))
        print("-----------------------------------------------------------------")
        
        
    def st_pyephem_epoch(self):
        """ return pyephem time string 
        """
        return "%4d/%02d/%02d %02d:%02d:%04.1f" % (self.yyyy,self.mon,self.dd,self.hh,self.min,self.sec)          
                    
    def st_snx_epoch(self):
        """ return SINEX time string 
        """
        return "%02d:%03d:%05d" % (self.yy,self.doy,self.dsec)          
        
    def st_iso_epoch(self,ndecimal=0):
        """Print iso time string
        """
        if ndecimal >0:
            format_str = "%4.0f-%02.0f-%02.0fT%02.0f:%02.0f:%"+("%02d.%1d" % (ndecimal+3,ndecimal))+'fZ'
        else:
            format_str = "%4.0f-%02.0f-%02.0fT%02.0f:%02.0f:%02.0fZ"

        return (format_str % (self.yyyy,self.mon,self.dd,self.hh,self.min,self.sec))        

    def __lt__(self, autre) :
        """Surcharge de <"""
        return self.mjd < autre.mjd
        
    def __gt__(self, autre) :
        """Surcharge de >"""
        return self.mjd > autre.mjd
        
    def __sub__(self, other):
        """
        Subtract a gpstime to a gpstime, or a timedelta in seconds
        """
        if isinstance(other, gpstime):
            return (self.mjd-other.mjd)*86400.0
        else:
            self.add_s(- other)
        
def test():
    
   # t1=gpstime()
    #t1.ymdhms_t('1980',1,6,0,0,1)
    #t1.print_dates()
    
    t2=gpstime()
    #t2.just_now()
    t2.ymdhms_t(2015,8,5,23,2,0.000001)
    t2.print_dates()  
    
    t2.ymdhms_t(2015,8,5,23,2,0.000000001)
    t2.print_dates()
    
    t2.ymdhms_t(2015,8,5,23,2,0)
    t2.print_dates()
    
    #print("Dates comparisons :")  
    #print("t1 < t2 : %s" % (t1 < t2))      
    #print("t1 > t2 : %s" % (t1 > t2))
    #print("-----------------------------------------------------------------")  
    
    #print("Dates modifications :")  
    #print("t2.add_s(43200.0) : ")      
    #t2.add_s(43200.0)
    #t2.print_dates()
    
    
    #print("Duration between t1 and t2 (t2 - t1) : %.3f s" % (t2 - t1))
    #print("t2 - 4500 (seconds) : ")
    #t2 - 4500.0
    #t2.print_dates()
    
    t0=gpstime()
    t0.yyyyddds_t(2014,342,0);
    t0.add_h(6.7)
    t0.add_day(6.7)
    
    print(t2.wsec+1.4)
    t2.print_dates()
    
    print(t2.st_pyephem_epoch())
    
    t2.wk00().add_s(86400).add_day(1.5).add_h(1.23).h00().add_s(12.455)
    t2.print_dates()
if __name__ == "__main__":
    
    test()    
 
