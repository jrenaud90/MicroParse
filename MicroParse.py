# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 21:08:13 2014
@author: jrenaud
"""
from html.parser import HTMLParser
from numpy import sin,arcsin,cos,pi,arccos
import os,urllib,datetime
vers = '1.0.5p'
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
class microevent:
    version = '0.4.5p'
    versionDate = '8-11-2014'
    
    def __init__(self,a,u,s,r,d,tmj,tmu,tu,umn,am,dma,fbl,ibl,io):
        self.active = a
        self.html = u
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
        try:
            string = str(string)
        except ValueError:
            raise
        if clean_string(string) in self.__dict__:
            setattr(self,string,value)
        else:
            print('Invalid String: '+ string)
            raise ValueError
            
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
        VisibData = (IsVis,alt,azmu)
        return VisibData
        
    def parseMinimumMag(self,MinMag):
        if float(self.i_o)< MinMag:
            return True
        else:
            return False
        
    def parseFuture(self,futureDate):
        if (float(self.t_max_hjd)-futureDate) >= 0:
            return True
        else:
            return False
            
    def parse(self,lonng,lat,utc,minmag,minALT,OnlyActive,OnlyFuture):
        #Long and Lat must be in decimal degrees eg: 23.210012
        #UTC must be a datetime object.
        #minmag should be in conventional units.
        #minALT should be in degrees 0-90
        #OnlyActive and OnlyFuture should be 1 for yes, 0 for no
        rejected = False
        completed = False
        VisibData = self.parseVisibility(lonng,lat,utc,minALT)
        while True:
            if OnlyFuture:
                currentJD = datetime2String_Num(utc,'jd')
                if not self.parseFuture(currentJD):
                    rejected = True
                    break
            if OnlyActive:
                if not self.active:
                    rejected = True
                    break
            if not VisibData[0]:
                rejected = True
                break
            if not self.parseMinimumMag(minmag):
                rejected = True
                break
            completed = True
            break
        if rejected:
            return (False,0,0)
        if completed and not rejected:
            return VisibData
        
    def print2CSV(self,compact,filepath,time,alt,azmu):
        if os.path.isfile(filepath+'output.csv'):
            with open(os.path.join(filepath,'output.csv'),'a') as csv:
                csv.write(self.__str__(time,alt,azmu,True))
                pass
        else:
            with open(os.path.join(filepath,'output.csv'),'w') as csv:
                if compact:
                    csv.write('Active,Date-Time(UTC),Alt,Azmu,HTML,RA(J2000),DEC(J2000),T_MAX(UT),tau,U_min,D_mag,f_bl,I_bl,I_o\n')
                    csv.write(self.__str__(time,alt,azmu,True))
                else:
                    csv.write('Active,Date-Time(UTC),Alt,Azmu,HTML,StarNo,RA(J2000),DEC(J2000),T_MAX(HJD),T_MAX(UT),tau,U_min,A_MAX,D_mag,f_bl,I_bl,I_o\n')
                    csv.write(self.__str__(time,alt,azmu,False))
                pass
    def __str__(self,time,alt,azmu,compact=False):
        if compact:
            return str(self.active)+','+datetime2String_Num(time,'s')+','+str(alt)+','+str(azmu)+','+str(self.html)+','+str(self.ra)+','+str(self.dec)+','+str(self.t_max_ut)+','+str(self.tau)+','+str(self.u_min)+','+str(self.d_mag)+','+str(self.i_bl)+','+str(self.i_o)+'\n'
        else:
            return str(self.active)+','+datetime2String_Num(time,'s')+','+str(alt)+','+str(azmu)+','+str(self.html)+','+str(self.starno)+','+str(self.ra)+','+str(self.dec)+','+str(self.t_max_hjd)+','+str(self.t_max_ut)+','+str(self.tau)+','+str(self.u_min)+','+str(self.a_max)+','+str(self.d_mag)+','+str(self.f_bl)+','+str(self.i_bl)+','+str(self.i_o)+'\n'

                
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
                
                
class log_class():
    ''' Log class used to create, update, save program logs. 
        Version 1.0 JPR 7-24-15
    '''
    def __init__(self,log_directory,function_name,use_timestamp=True,write_opening_lines=True):
        ''' Construction of Log class. Ensures that directory exists, gets opening timestamp, opens file obj, writes opening lines. '''
        # Ensure that directory exists
        import os
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        if use_timestamp:
            from datetime import datetime
            import time
            self.time = time
            self.datetime = datetime
            Start_Time = self.time.time()
            Time_Stamp = self.datetime.fromtimestamp(Start_Time).strftime('%Y%m%d_%H%M%S')
        try:
            self.full_path = os.path.join(log_directory,'Log_'+function_name+'_'+Time_Stamp+'.log')
        except TypeError:
            raise
        # Open file obj.        
        self.file_obj = open(self.full_path,'w')
        # Write opening lines
        if write_opening_lines:
            self.write(function_name + ' log file. Created on ' + Time_Stamp)
        
    def write(self,input,auto_line=True,include_timestamp=False):
        ''' Write an input line(s) to the log file. '''
        if include_timestamp:
            Start_Time = self.time.time()
            Current_Time_Str = self.datetime.fromtimestamp(Start_Time).strftime('%H%M%S') + ': '
        else:
            Current_Time_Str = ''
        if auto_line:
            self.file_obj.write(Current_Time_Str + input+'\n')
        else:
            self.file_obj.write(Current_Time_Str + input)
            
    def close(self,write_final_line=True):
        ''' Calls self.__del__ '''
        self.__del__(write_final_line)
    
    def __call__(self,input,auto_line=True,include_timestamp=False):
        ''' Write an input line(s) to the log file. Implemented as a function call. '''
        self.write(input,auto_line,include_timestamp)
    
    def __del__(self,write_final_line=True):
        ''' Writes final log command including final timestamp, and closes file, then deletes instance. '''
        if write_final_line:
            End_Time = self.time.time()
            Final_Time_Stamp = self.datetime.fromtimestamp(End_Time).strftime('%Y%m%d_%H%M%S')
            self.write('-~-~->>> LOG CLOSING AT: ' + Final_Time_Stamp + ' <<<-~-~-')
        self.file_obj.close()
        del self
     
    def __bool__(self):
        ''' Will return True if log file is open '''
        return not self.file_obj.closed
    
    def __str__(self):
        ''' Return string representing log file '''
        return 'log_class instance located at ' + self.full_path + '. Current open status: ' + str(self.__bool__())
        
    
def MAKE_WORKING_DIR(Dir_Name,Time_Stamp=True,Use_Cwd_Asbase=True,**kwargs):
    ''' Small function that creates a working directory. 
        Version 1.0 JPR 7-24-15
        Inputs (*Optional): (Dir_Name,Time_Stamp=True,Use_Cwd_Asbase=True)
            - Dir_Name == Name of new directory.
            - Time_Stamp == will append timestamp of when this function is called to directory.
            - Use_Cwd_Asbase == will use current working directory as the base directory (you new directory will be a sub directory of this space).
            - kwarg('base_cwd') == if Use_Cwd_Asbase is False, please send directory in with this kwarg.
        Outputs: Directory_Path '''
    import os
    if Time_Stamp:
        from datetime import datetime
        import time
        Start_Time = time.time()
        Time_Stamp = datetime.fromtimestamp(Start_Time).strftime('%Y%m%d_%H%M%S')
    else:
        Time_Stamp = ''
    if Use_Cwd_Asbase:
        Base_Dir = os.getcwd()
    else:
        Base_Dir = kwargs.get('base_cwd','')
    try:
        D_Name = Dir_Name + Time_Stamp
        Output_Directory = os.path.join(Base_Dir,D_Name)
    except TypeError:
        raise
    # Create Directory Path
    if not os.path.exists(Output_Directory):
        os.makedirs(Output_Directory)
    return Output_Directory
        
def MainGrab():
    vers = '1.0.5'
    lmo = '7-24-15'
    # Create Workind Directory with timestamp.
    Working_Dir = MAKE_WORKING_DIR('MicroParseRun_')
    #MakeLog
    log = log_class(Working_Dir,'MicroParse_')
    log('Exoplanet Micro Lens Parsing Log\nVersion '+vers+', by Joe Renaud. Last modified on: '+lmo)
    Website = 'http://ogle.astrouw.edu.pl/ogle4/ews/ews.html'
    log('Initializing...')
    log('Opening: ' + Website,True,True)
    kstr = DownloadHTMLtext(Website,log,Working_Dir)
    global htmldata
    with open(os.path.join(Working_Dir,'htmlparse.tmp'),'w') as htmldata:
        parser = MyHTMLParser()
        log('Superstring passed into parser function')
        parser.feed(kstr)
        pass
    log('OnlyParse Function called')
    log('MainGrab Function Finished')
    OnlyParse(Working_Dir,log)
    
def OnlyParse(CurrentPath,log,**kwargs):
    import time
    Parameters = queryUser()
    compactPrintout = kwargs.get('compact_print',False)
    log('OnlyParse function is now running...')
    global htmldata
    global datastore
    with open(os.path.join(CurrentPath,'htmlparse.tmp'),'r') as htmldata:
        log('Data found!')
        with open(os.path.join(CurrentPath,'ParseOutput.tmp'),'w') as datastore:
            ParseDataFile(htmldata,datastore,log,CurrentPath)
            pass
        pass
    with open(os.path.join(CurrentPath,'ParseOutput.tmp'),'r') as datastore:
        events = inputintoobject(datastore,log)
        log('Events Found')
        pass
    times = dateFinder('y',Parameters['days_out'],Parameters['minute_separation'])
    log('Times Found',True,True)
    log('Running through events and times')
    log('events: ' + str(len(events)))
    log('times: ' + str(len(times)))
    timerr = len(times)
    print('25% Complete')
    dt = float((100-25)/timerr)
    perc = 25
    pold = 25
    loop_pre_time = time.time()
    for time_step in times:
        perc = perc + dt
        pnew = int(perc)
        if pnew != pold:
            print(str(pnew) + '% Complete')
            pold = pnew
        for event in events:
            data = event.parse(Parameters['longitude'],Parameters['latitude'],time_step,Parameters['minimum_magnitude'],Parameters['minimum_altitude'],Parameters['only_active'],Parameters['only_future'])
            if data[0]:
                event.print2CSV(compactPrintout,CurrentPath,time_step,data[1],data[2])
    log('Parser Finished! Total Loop Time: ' + str(round(time.time()-loop_pre_time,1)))
    del log
    print('-->>MicroParse Done<<--')
    
def queryUser():
    default_QRY = clean_string(input('Do you want to use Default variables (Y/N)? '))
    Parameters = {}
    if default_QRY in ['n','no']:
        Parameters['longitude'] = float(clean_string(input('Observatory Longitude (def=-77.305325): ')))
        Parameters['latitude'] = float(clean_string(input('Observatory Latitude (def=38.828176): ')))
        Parameters['days_out'] = int(clean_string(input('How many days from now do you want to parse to (def=30): ')))
        perc_tmp = float(clean_string(input('How many times a night do you want to check (def=9): ')))
        Parameters['minute_separation'] = int((9*60)/perc_tmp)
        Parameters['minimum_altitude'] = float(clean_string(input('What is the lowest altitude you can observe at (in degrees) (def=20): ')))
        Parameters['minimum_magnitude'] = float(clean_string(input('What is the minimum magnitude you can observe (def=17): ')))
        OnlyActive = clean_string(input('Only Active Events? (def=y): '))
        if OnlyActive in ['y','yes']:
            Parameters['only_active'] = True
        else:
            Parameters['only_active'] = False
        OnlyFuture = clean_string(input('Look at only future maximums? (def=y): '))
        if OnlyFuture in ['y','yes']:
            Parameters['only_future'] = True
        else:
            Parameters['only_future'] = False
    else:
        Parameters['minute_separation'] = int(270) #minutes, I would keep this between 30 - 280
        Parameters['longitude'] = -77.305325 #degrees East
        Parameters['latitude'] = 38.828176 #degrees North
        Parameters['days_out'] = 60
        Parameters['minimum_magnitude'] = 17 #Minimum Magnitude to detect
        Parameters['minimum_altitude'] = 20 #Degrees above the horizon
        Parameters['only_active'] = True #Look for only Active Events
        Parameters['only_future'] = True #Only look at future maximums in the events
    return Parameters
#######Back Ground Files#######

def inputintoobject(data,log):
    import pdb
    log('inputintoobject func called.',True,True)
    log('CSVfile made')
    log('    --- PARSING INFORMATION ---')
    lines=data.readlines()
    events = []
    for i, line in enumerate(lines):
        if line == ' ----NEW EVENT----\n':
            if lines[i+1] == '\n':
                log.write('bad sector found, skipped: '+str(i)+'='+line)
            else:
                if lines[i+1]=='LIVE!----------------\n':
                    active = True;
                    skip = 1;
                else:
                    active = False;
                    skip = 0;
                url = lines[i+1+skip]
                url = url[0:-1]
                starno = lines[i+2+skip]
                starno = starno[0:-1]
                RA = lines[i+3+skip]
                RA = RA[0:-1]
                DEC = lines[i+4+skip]
                DEC = DEC[0:-1]
                tmaxhj = lines[i+5+skip]
                tmaxhj = tmaxhj[0:-1]
                tmaxut = lines[i+6+skip]
                tmaxut = tmaxut[0:-1]
                tau = lines[i+7+skip]
                tau = tau[0:-1]
                umin = lines[i+8+skip]
                umin = umin[0:-1]
                amax = lines[i+9+skip]
                amax = amax[0:-1]
                dmag = lines[i+10+skip]
                dmag = dmag[0:-1]
                fbl = lines[i+11+skip]
                fbl = fbl[0:-1]
                ibl = lines[i+12+skip]
                ibl = ibl[0:-1]
                io = lines[i+13+skip]
                io = io[0:-1]
                url = 'http://ogle.astrouw.edu.pl/ogle4/ews/'+url
                events.append(microevent(active,url,starno,RA,DEC,tmaxhj,tmaxut,tau,umin,amax,dmag,fbl,ibl,io))
    log('    --- PARSING END ---')
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
    log('    '+ str(newevents)+ ' New Event(s) Found!')
    log('    ' + str(actives) + ' Active Event(s) Found!')
                
def DownloadHTMLtext(html,log,CurrentPath):
    import os
    log('DownloadHTMLtext Function called',True,True)
    HtmlData = urllib.request.urlopen(html)
    log('HTML Data Downloaded')
    path = os.path.join(CurrentPath,'html.tmp')
    with open(path,'wb') as filetmp:
        for line in HtmlData:
            filetmp.write(line)
        pass
    log('HTML Data Saved Locally')
    with open(path,'r') as html1:
        log.write('Reading ' + path + 'as var: html1')
        kstr = ''
        for line in html1:
            kstr = kstr + line #Make large string of the html file
        pass
    log('HTML data passed into super-string')
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
        print('Sorry, this feature is not yet implemented.') # TODO
    return UTCtimes
    

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
    A = arccos(tmp2)
    #Now lets convert back to degrees the new values:
    Alt = Alt*(180/pi)
    A = A*(180/pi)
    if sin(HA)<0:
        Azmu = A
    else:
        Azmu = 360 - A
    Data = [Alt,Azmu]
    return Data

# TODO
#def outputCSV2GoogleCSV(Path,compact):
#    ##Not working atm
#    with open(Path+'output.csv','rb') as inputcsvH:
#        with open(Path+'outputUpload.csv','w') as outputcsvH:
#            with deleteContent(outputcsvH) as outputcsv:
#                outputcsv.write('Subject, Start Date, Start Time, End Date, End Time, All Day Event, Description, Location, Private\n')
#                inputcsv = csv.reader(inputcsvH, delimiter=',', quotechar='|')
#                for row in inputcsv:
#                    if testrow(row,now,mindeg,toolate,tooearly,TimePre,TimePost):
#                        [btrandate,btrantime] = jd2gd(float(row[6])-TimePre*60*0.000011574)
#                        [etrandate,etrantime] = jd2gd(float(row[14])+TimePost*60*0.000011574)
#                        [mtrandate,mtrantime] = jd2gd(float(row[10]))
#                        Desc1 = '\"'+row[1] + '; Prediction URL: \'' + row[0] + '\'; Begin-Transit: ' + row[4] + row[5]+',' + row[6] + '; '
#                        Desc2 = 'End-Transit: ' + row[12] + row[13]+',' + row[14] + '; '
#                        Desc3 = 'Location: RA=' + row[19] + ', DE=' + row[20] + '; '
#                        Desc4 = 'D: ' + row[15] + '; V: ' + row[16] + '; Depth(Mag): ' + row[17] + '\"'
#                        Desc = Desc1 + Desc2 + Desc3 + Desc4
#                        line = row[1]+' (mag=' + row[17] + '),'+btrandate+','+btrantime+','+etrandate+','+etrantime+',False,'+Desc+',GMUObservatory,'+'False'
#                        outputcsv.write(line + '\n')
#                pass
#            pass
#        pass

def clean_string(string):
    if type(string) == type('hello'):
        string = string.lower()
        string = string.strip()
        return string
    else:
        raise ValueError

if __name__ == '__main__':
    print('Welcome to MicroParse version 1.x!')
    MainGrab()