# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 21:08:13 2014
@author: jrenaud
"""

from HTMLParser import HTMLParser
from numpy import sin,arcsin,cos,pi
import os,urllib2,datetime
vers = '0.8.3n'
####Main Files####
#==============================================================================
# Run MainGrab() if you want to run the parser from scratch, downloading new 
# files.
#
# Run OnlyParse if you do not want to download files. However, follow these instructions:
#  - First make a folder with the data you want to parse saved as 'htmlparse.tmp'
#  - Record the file path to the main folder holing the htmlparse.tmp, this is 
#  - where all data will be saved.
#  - Run:: 'log = logMaker(path)' where path is the aforementioned path
#  - Now run:: 'OnlyParse(path,log)' where path is as mentioned, and log is the 
#  - variable holding the logMaker object.
#==============================================================================
def MainGrab():
    FolderPath = 'C:/MicroLensParse/'
    if not os.path.exists(FolderPath):
        os.makedirs(FolderPath)
    CurrentPath = FolderPath + 'Run_' + UTC2str(CurrentUTC()) + '/'
    os.makedirs(CurrentPath)
    #MakeLog
    log = LogMaker(CurrentPath)
    log.write('Exoplanet Micro Lens Parsing Log\nVersion '+vers+', by Joe Renaud\n')
    Website = 'http://ogle.astrouw.edu.pl/ogle4/ews/ews.html'
    log.write('Initializing...\n')
    log.write('Opening: ' + Website +'\n')
    kstr = DownloadHTMLtext(Website,log,CurrentPath)
    global htmldata
    with open(CurrentPath+'htmlparse.tmp','w') as htmldata:
        parser = MyHTMLParser()
        log.write('Superstring passed into parser function\n')
        parser.feed(kstr)
        pass
    log.write('OnlyParse Function called\n')
    log.write('MainGrab Function Finished\n')
    OnlyParse(CurrentPath,log)
def OnlyParse(Path,log):
    daysOut = 30 #Days out from today to search
    precision = 30 #minutes, I would keep this between 30 - 240
    ObservLong = -77.305325 #degrees East
    ObservLat = 38.828176 #degrees North
    MinMag = 20 #Minimum Magnitude to detect
    minALT = 15 #Degrees above the horizon
    OnlyActive = 0 #Look for only Active Events
    compactPrintout = 'y'
    log.write('Previous Log file found\n')
    log.write('OnlyParse function is now running...\n')
    global htmldata
    global datastore
    with open(Path+'htmlparse.tmp','r') as htmldata:
        log.write('Data found!\n')
        with open(Path + 'ParseOutput.tmp','w') as datastore:
            ParseDataFile(htmldata,datastore,log,Path)
            pass
        pass
    with open(Path + 'ParseOutput.tmp','r') as datastore:
        events = inputintoobject(datastore,log)
        log.write('Events Found')
        pass
    times = dateFinder('y',daysOut,precision)
    log.write('Times Found')
    log.write('Running through events and times')
    for event in events:
        for time in times:
            data = event.parse(ObservLong,ObservLat,time,MinMag,minALT,OnlyActive)
            if data[0]:
                event.print2CSV(compactPrintout,Path,time,data[1],data[2])
    log.write('Parser Finished')
    
#######Back Ground Files#######
    
def LogMaker(CurrentPath):
    logpath = CurrentPath + 'Output.log'
    log = open(logpath,'w')
    #
    return log    
def inputintoobject(data,log):
    log.write('CSVfile made\n')
    lines=data.readlines()
    events = []
    for i, line in enumerate(lines):
        if line == ' ----NEW EVENT----\n':
            if lines[i+1] == '\n':
                log.write('bad sector found, skipped \n')
            else:
                if lines[i+1]=='LIVE!----------------\n':
                    active = '1';
                    skip = 1;
                else:
                    active = '0';
                    skip = 0;
                url = lines[i+1+skip]
                starno = lines[i+2+skip]
                RA = lines[i+3+skip]
                DEC = lines[i+4+skip]
                tmaxhj = lines[i+5+skip]
                tmaxut = lines[i+6+skip] 
                tau = lines[i+7+skip]
                umin = lines[i+8+skip]
                amax = lines[i+9+skip]
                dmag = lines[i+10+skip]
                fbl = lines[i+11+skip]
                ibl = lines[i+12+skip]
                io = lines[i+13+skip]
                events.append(microevent(active,url,starno,RA,DEC,tmaxhj,tmaxut,tau,umin,amax,dmag,fbl,ibl,io))
	return events
				
def ParseDataFile(htmldata,datastore,log,Path):
    nextline = 0
    nextlinego = 0
    newitem = 0
    newevents = 0
    actives = 0
    for line in htmldata:
        if newitem == 1:
            datastore.write('\n\n ----NEW EVENT----\n')
            newevents += 1
        elif nextline ==1:
            strr = line[7:];
            if not strr == '= RIGHT\n':
                strr = strr[1:]
                datastore.write(strr)
        elif nextlinego == 1:
            datastore.write('LIVE!----------------\n')
            actives +=1
        
        if line[0:9] == '::TAG: td':
            nextline = 1;
        elif line[0:8] == '::TAG: a':
            nextline = 1;
        elif line[0:10] == '::TAG: img':
            nextlinego = 1;
        elif line[0:9] == '::TAG: tr':
            newitem = 1;
        else:
            nextline = 0;
            nextlinego = 0;
            newitem = 0;       
    log.write('--- '+ str(newevents)+ ' New Event(s) Found!\n')
    log.write('--- ' + str(actives) + ' Active Event(s) Found!\n')
class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        if len(data) > 1:
            htmldata.write('::DATA: ' + data + '\n')
    def handle_starttag(self, tag, attrs):
        htmldata.write('Item: \n')
        htmldata.write('::TAG: ' + tag + '\n')
        for attr in attrs:
            if len(attr)<2:
                htmldata.write('\t' + attr + '\n')
            else:
                st1 = attr[0]
                st2 = attr[1]
                htmldata.write('\t' + st1 + ' = ' + st2 + '\n')
def DownloadHTMLtext(html,log,CurrentPath):
        HtmlData = urllib2.urlopen(html)
        log.write('HTML Data Downloaded\n')
        path = CurrentPath+'html.tmp'
        with open(path,'w') as filetmp:
            for line in HtmlData:
                filetmp.write(line)
            pass
        log.write('HTML Data Saved Locally\n')
        with open(path,'r') as html1:
            log.write('Reading ' + path + 'as var: html1\n')
            kstr = ''
            for line in html1:
                kstr = kstr + line #Make large string of the html file
            pass
        log.write('HTML data passed into super-string\n')
        return kstr
def CurrentUTC():
    #Needs imported datetime
    x = datetime.datetime.utcnow()
    return x
def UTC2str(UTC):
    y=str(UTC.year)
    if UTC.month <10:
        m = '0' + str(UTC.month)
    else:
        m = str(UTC.month)
    if UTC.day <10:
        d = '0' + str(UTC.day)
    else: 
        d = str(UTC.day)
    if UTC.hour <10:
        hr = '0' + str(UTC.hour)
    else:
        hr = str(UTC.hour)
    if UTC.minute <10:
        mn = '0' + str(UTC.minute)
    else:
        mn = str(UTC.minute)
    if UTC.second <10:
        sc = '0' + str(UTC.second)
    else:
        sc = str(UTC.second)
    Full = m+d+y+'-'+hr+mn+sc
    return Full
def dateFinder(NowQ,days,precision):
    #days - out from now
    #precision in minutes 
    starthourUTC = '00:00'
    endhourUTC = '09:00'
    daysinmonths = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    #Note, code does not account for leap years at this stage.
    if NowQ == 'y':
        now = datetime.datetime.utcnow()
        syear = now.year
        smonth = now.month
        sday = now.day
        if now.hour >= 0 and now.hour <= 4:
            if sday == 1:
                if smonth == 1:
                    syear = syear -1
                    smonth = 12
                else:
                    smonth = smonth - 1
                sday = daysinmonths[smonth]
            else:
                sday = sday - 1
        shour = int(starthourUTC[0:2])
        smin = int(starthourUTC[3:len(starthourUTC)])
        ehour = int(endhourUTC[0:2])
        emin = int(endhourUTC[3:len(endhourUTC)])
        thour = shour
        tmin = smin
        tday = sday
        tmonth = smonth
        tyear = syear
        UTCtimes = []
        for i in range(1,days):
            thour = shour
            tmin = smin
            if tday > daysinmonths[tmonth]:
                tday = tday - daysinmonths[tmonth]
                tmonth = tmonth + 1
                if tmonth > 12:
                    tmonth = 1
                    tyear = tyear + 1
            while thour < ehour or tmin < emin:
                UTCtimes.append(datetime.datetime(tyear,tmonth,tday,thour,tmin))
                tmin = tmin+precision
                while tmin > 59:
                    thour = thour + 1
                    tmin = tmin - 60
            tday = tday + 1
    else:
        print 'Sorry, this feature is not yet implemented.'
    return UTCtimes
class microevent:
	version = '0.3.6n'
	versionDate = '8-11-2014'
	def __init__(self,a,u,f,s,r,d,tmj,tmu,umn,tu,am,dma,fbl,ibl,io):
		self.active = a
		self.html = u
		self.field = f
		self.starno = s
		self.ra = r
		self.dec = d
		self.t_max_hjd = tmj
		self.t_max_ut = tmu
		self.u_min = umn
		self.tau = tu
		self.a_max = am
		self.d_mag = dma
		self.f_bl = fbl
		self.i_bl = ibl
		self.i_o = io
	def changeValue(self,string,value):
		#Possible Input Strings:
		#	==active,html,field,starno,ra,dec,t_max_hjd,t_max_ut,tau,a_max,d_mag,f_bl,i_bl,i_o
		if string == 'active':
			self.active = value
		elif string == 'html':
			self.html = value
		elif string == 'field':
			self.field = value
		elif string == 'starno':
			self.starno = value
		elif string == 'ra':
			self.ra = value
		elif string == 'dec':
			self.dec = value
		elif string == 't_max_hjd':
			self.t_max_hjd = value
		elif string == 't_max_ut':
			self.t_max_ut = value
		elif string == 'tau':
			self.tau = value
		elif string == 'a_max':
			self.a_max = value
		elif string == 'd_mag':
			self.d_mag = value
		elif string == 'f_bl':
			self.f_bl = value
		elif string == 'i_bl':
			self.i_bl = value
		elif string == 'i_o':
			self.i_o = value
		elif string == 'u_min':
			self.u_min = value
		else:
			print 'Invalid string'
	def parseVisibility(self,lonng,lat,UTC,minALT):
          #Methods based upon the great website: 
          # http://www.stargazing.net/kepler/altaz.html accesed 8/2014
          # Please cite the above in any publications
          RA = RAtoHours_Deg(self.ra,'y')
          DEC = DECtoDeg(self.dec,'n')
          d = daysFromJ2000(UTC)
          LST = LST_finder(d,UTC,lonng)
          HA = HA_finder(RA,LST)
          AltAz = AltAzmu_finder(RA,DEC,HA,lat)
          alt = AltAz[0]
          azmu = AltAz[1]
          if alt < minALT:
              IsVis = False
          else:
              IsVis = True
          VisibData = [IsVis,alt,azmu]
          return VisibData
		#return Visibility
	def parseMinimumMag(self,MinMag):
		if float(self.i_o)+float(self.d_mag) > MinMag:
			MinMagTest = True
		else:
			MinMagTest = False
		return MinMagTest
	def parse(self,lonng,lat,utc,minmag,minALT,OnlyActive):
         if OnlyActive == 1:
             if int(self.active) == 1:
                 nxt = 1
             else:
                 nxt = 0
         else:
             nxt = 1
         if nxt == 1:
             VisibData = self.parseVisibility(lonng,lat,utc,minALT)
             if (minmag == 'NA' and VisibData[0]):
                 parsepass = True
             elif (self.parseMinimumMag(minmag) and VisibData[0]):
                 parsepass = True
             else:
                 parsepass = False
             parsedata = [parsepass,VisibData[1],VisibData[2]]
         else:
             parsedata = [False,0,0]
         return parsedata
	def print2CSV(self,compact,filepath,time,alt,azmu):
         if compact == 'y':
             stringout = self.active+','+datetime2String_Num(time,'s')+','+str(alt)+','+str(azmu)+','+self.html+','+self.ra+','+self.dec+','+self.t_max_ut+','+self.tau+','+self.u_min+','+self.d_mag+','+self.i_bl+','+self.i_o+'\n'
         else:
             stringout = self.active+','+datetime2String_Num(time,'s')+','+str(alt)+','+str(azmu)+','+self.html+','+self.field+','+self.starno+','+self.ra+','+self.dec+','+self.t_max_hjd+','+self.t_max_ut+','+self.tau+','+self.u_min+','+self.a_max+','+self.d_mag+','+self.f_bl+','+self.i_bl+','+self.i_o+'\n'
         if os.path.isfile(filepath+'output.csv'):
             with open(filepath+'output.csv','a') as csv:
                 csv.write(stringout)
                 pass
         else:
             with open(filepath+'output.csv','w') as csv:
                 if compact == 'y':
                     csv.write('Active,Date-Time(UTC),Alt,Azmu,HTML,RA(J2000),DEC(J2000),T_MAX(UT),tau,U_min,D_mag,f_bl,I_bl,I_o\n')
                     csv.write(stringout)
                     pass
                 else:
                     csv.write('Active,Date-Time(UTC),Alt,Azmu,HTML,Field,StarNo,RA(J2000),DEC(J2000),T_MAX(HJD),T_MAX(UT),tau,U_min,A_MAX,D_mag,f_bl,I_bl,I_o\n')
                     csv.write(stringout)
                     pass
def datetime2String_Num(time,outputType):
    y = time.year
    m = time.month
    d = time.day
    h = time.hour
    mn = time.minute
    s = time.second
    if outputType == 's':
        output = str(m)+'-'+str(d)+'-'+str(y)+' '+str(h)+':'+str(mn)+':'+str(s)
    elif outputType == 'ymdx':
        mn = float(mn + s/60)
        h = float(h + m/60)
        d = float(d + h/24)
        output = [y,m,d]
    elif outputType == 'hx':
        m = m + s/60
        h = h + m/60
        output = h
    elif outputType == 'tonly':
        output = [h,mn,s]
    elif outputType == 'donly':
        output = [y,m,d]
    elif outputType == 'jd':
        y = float(y)
        m = float(m)
        d = float(d)
        mterm=int((m-14)/12)
        aterm=int((1461*(y+4800+mterm))/4)
        bterm=int((367*(m-2-12*mterm))/12)
        cterm=int((3*int((y+4900+mterm)/100))/4)
        j=aterm+bterm-cterm+d
        j -= 32075
        #offset to start of day
        j -= 0.5
        #    print "h/m/s: %f/%f/%f"%(hr,min,sec)
        #Apply the time
        output = j + (h + (mn + (s/60.0))/60.0)/24.0
    return output
def DECtoDeg(string,radQ):
    if string[2] == ':':
        pn = 'pos'
        D = float(string[0:2])
        M = float(string[3:5])
        S = float(string[6:len(string)])
    else:
        pn = 'neg'
        D = float(string[1:3])
        M = float(string[4:6])
        S = float(string[7:len(string)])
    M = M + S/60
    D = D + M/60
    if pn == 'neg':
        D = 360-D
    if radQ =='y':
        out = D*(pi/180)
    else:
        out = D
    return out
def RAtoHours_Deg(string,ConvrtDegQ):
    H = float(string[0:2])
    M = float(string[3:5])
    S = float(string[6:len(string)])
    M = M + S/60
    H = H + M/60
    if ConvrtDegQ == 'y':
        out = H*15
    else:
        out = H
    return out
def daysFromJ2000(UTC):
    #input is a datetime object in UTC
    #J2000 is defined as 1200 hrs UT on Jan 1st 2000 AD
    ##Days to beginning of year
    DaystoYear = {1998:-731.5,1999:-366.5,2000:-1.5,2001:364.5,2002:729.5,2003:1094.5,\
                  2004:1459.5,2005:1825.5,2006:2190.5,2007:2555.5,2008:2920.5,2009:3286.5,\
                  2010:3651.5,2011:4016.5,2012:4381.5,2013:4747.5,2014:5112.5,2015:5477.5,\
                  2016:5842.5,2017:6208.5,2018:6573.5,2019:6938.5,2020:7303.5,2021:7669.5}
    ##Days to beginning of month:
    DaystoMonthLY = {1:0,2:31,3:60,4:91,5:121,6:152,7:182,8:213,9:244,10:274,11:305,12:335}
    DaystoMonthNoLY = {1:0,2:31,3:59,4:90,5:120,6:151,7:181,8:212,9:243,10:273,11:304,12:334}
    out = datetime2String_Num(UTC,'ymdx')
    d = out[2]
    m = out[1]
    y = out[0]
    if y == 2016 or y == 2020:
        daytomonth = DaystoMonthLY[m]
    else:
        daytomonth = DaystoMonthNoLY[m]
    days = d + daytomonth + DaystoYear[y]
    return days
def LST_finder(d,Ut,lonng):
    # Based upon the number of days from the epoch J2000
#==============================================================================
# LST = 100.46 + 0.985647 * d + long + 15*UT
# 
#       d    is the days from J2000, including the fraction of
#            a day
#       UT   is the universal time in decimal hours
#       long is your longitude in decimal degrees, East positive.
#       
# Add or subtract multiples of 360 to bring LST in range 0 to 360 degrees.
# and this formula gives your local siderial time in degrees. You can divide by 
# 15 to get your local siderial time in hours, but often we leave the figure in 
# degrees. The approximation is within 0.3 seconds of time for dates within 100 
# years of J2000.
#==============================================================================
    dcHours = datetime2String_Num(Ut,'hx')
    lstdeg = 100.46+(0.985647*d)+lonng+(15*dcHours)
    if lstdeg < 0:
        while lstdeg < 0:
            lstdeg = lstdeg + 360
    elif lstdeg > 360:
        while lstdeg > 360:
            lstdeg = lstdeg - 360
    lst = lstdeg
    return lst
def HA_finder(RA,LST):
    #Both RA and LST need to be in degrees 0 - 360.
    #Will output HA in degrees 0 - 360
    HAtmp = LST - RA
    if HAtmp < 0:
        while HAtmp < 0:
            HAtmp = HAtmp + 360
    elif HAtmp > 360:
        while HAtmp > 360:
            HAtmp = HAtmp - 360
    HA = HAtmp
    return HA
def AltAzmu_finder(RA,DEC,HA,LAT):
    #RA,DEC,HA should all be in degrees. However, numpy's sin/cos defaults to 
    #Radians so we need to convert before use.
    RA = RA*(pi/180)
    DEC = DEC*(pi/180)
    HA = HA*(pi/180)
    LAT = LAT*(pi/180)
    tmp1 = sin(DEC)*sin(LAT)+cos(DEC)*cos(LAT)*cos(HA)
    Alt = arcsin(tmp1)
    tmp2 = (sin(DEC)-sin(Alt)*sin(LAT))/(cos(Alt)*cos(LAT))
    A = arccost(tmp2)
    #Now lets convert back to degrees the new values:
    Alt = Alt*(180/pi)
    A = A*(180/pi)
    if sin(HA)<0:
        Azmu = A
    else:
        Azmu = 360 - A
    Data = [Alt,Azmu]
    return Data