import os
import urllib.request
from numpy import sin
from numpy import cos
from numpy import arcsin as asin
from numpy import arccos as acos

# Constants
deg2rad = (pi/180)
# Days to beginning of year
DaystoYear = {1998:-731.5,1999:-366.5,2000:-1.5,2001:364.5,2002:729.5,2003:1094.5,\
              2004:1459.5,2005:1825.5,2006:2190.5,2007:2555.5,2008:2920.5,2009:3286.5,\
              2010:3651.5,2011:4016.5,2012:4381.5,2013:4747.5,2014:5112.5,2015:5477.5,\
              2016:5842.5,2017:6208.5,2018:6573.5,2019:6938.5,2020:7303.5,2021:7669.5}
# Days to beginning of month:
DaystoMonthLY = {1:0,2:31,3:60,4:91,5:121,6:152,7:182,8:213,9:244,10:274,11:305,12:335}
DaystoMonthNoLY = {1:0,2:31,3:59,4:90,5:120,6:151,7:181,8:212,9:243,10:273,11:304,12:334}

class MicroEvent:



    def __init__(self, parms):
        # Parms should have: a, u, s, r, d, tmj, tmu, tu, umn, am, dma, fbl, ibl, io
        self.parms = parms
        self.name = self.parms['url'].split('/')[-1].split('.')[0].upper()
        
        # Preform Conversions
        self.parms['RA_hours_degs'] = RAtoHours(self.parms['RA'], ConvrtDegQ=True)
        self.parms['RA_hours_rads'] = deg2rad*self.parms['RA_hours_degs']
        self.parms['DEC_degs'] = DECtoDeg(self.parms['DEC'], convert_radians=False)
        self.parms['DEC_rads'] = deg2rad*self.parms['DEC_degs']

    def changeValue(self, string, value):
        #Possible Input Strings:
        #	==active,html,field,starno,ra,dec,t_max_hjd,t_max_ut,tau,a_max,d_mag,f_bl,i_bl,i_o
        if string not in self.parms:
            raise Exception('Unknown MicroEvent Parameter, to change')
        else:
            self.parms[string] = value
            
    def parseVisibility(self, longde, latde, UTC, minALT):
        # Methods based upon the great website:
        # http://www.stargazing.net/kepler/altaz.html accesed 8/2014
        # Please cite the above in any publications
        # RA,DEC,HA should all be in degrees. However, numpy's sin/cos defaults to Radians so we need to convert before use.
        days_from_epoch = daysFromJ2000(UTC)
        LST = findLST(days_from_epoch, UTC, longde)
        HA_rads = deg2rad*findHA(self.parms['RA_hours_degs'], LST)
        alt, azmu = findALT_AZMU(self.parms['DEC_rads'], HA_rads, latde*deg2rad)
        if alt < minALT:
            IsVis = False
        else:
            IsVis = True
        return (IsVis, alt, azmu)
        
    def parseMinimumMag(self, MinMag):
        if self.parms['io_f'] < MinMag:
            out = True
        else:
            out = False
        return out
        
    def parseFuture(self, futureDate):
        if (self.parms['tmaxhj_f'] - futureDate) >= 0:
            out = True
        else:
            out = False
        return out
            
    def parse(self, longde, latde, UTC, minmag, minALT, OnlyActive=True, OnlyFuture=True, OnlyVisible=True):
        # Long and Lat must be in decimal degrees eg: 23.210012
        # UTC must be a datetime object.
        # minmag should be in conventional units.
        # minALT should be in degrees 0-90
        # OnlyActive and OnlyFuture should be booleans
        rejected = False
        completed = False
        visible, alt, azmu = self.parseVisibility(longde, latde, UTC, minALT)
        while True:
            if OnlyVisible:
                if not visible:
                    rejected = True
                    break
            if OnlyActive:
                if not self.parms['active']:
                    rejected = True
                    break
            if OnlyFuture:
                currentJD = datetime2String_Num(utc, 'jd')
                if not self.parseFuture(currentJD):
                    rejected = True
                    break
            if not self.parseMinimumMag(minmag):
                rejected = True
                break
            completed = True
            break
        if rejected:
            return (False, 0, 0)
        if completed and not rejected:
            return (True, alt, azmu)
        
    def print2CSV(self, csvfile, compact, time, alt, azmu):
        csvfile.write(self.saveSTR(time, alt, azmu, compact))

    def saveSTR(self, time, alt, azmu, compact=False):
        if compact:
            output = [str(self.parms['active']),
                      self.name,
                      datetime2String_Num(time,'s'),
                      str(alt),
                      str(azmu),
                      str(self.html),
                      str(self.ra),
                      str(self.dec),
                      str(self.t_max_ut),
                      str(self.tau),
                      str(self.u_min),
                      str(self.d_mag),
                      str(self.i_bl),
                      str(self.i_o)]
        else:
            output = [str(self.active),
                      self.name,
                      datetime2String_Num(time,'s'),
                      str(alt),
                      str(azmu),
                      str(self.html),
                      str(self.starno),
                      str(self.ra),
                      str(self.dec),
                      str(self.t_max_hjd),
                      str(self.t_max_ut),
                      str(self.tau),
                      str(self.u_min),
                      str(self.a_max),
                      str(self.d_mag),
                      str(self.f_bl),
                      str(self.i_bl),
                      str(self.i_o)]
        return output.join(',') + '\n'

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
    
def DECtoDeg(string, convert_radians=False):
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
    if convert_radians:
        out = D*(pi/180)
    else:
        out = D
    return out
    
def RAtoHours(string, ConvrtDegQ=True):
    H = float(string[0:2])
    M = float(string[3:5])
    S = float(string[6:len(string)])
    M = M + S/60
    H = H + M/60
    if ConvrtDegQ:
        out = H*15
    else:
        out = H
    return out
    
def daysFromJ2000(UTC):
    # Input is a datetime object in UTC
    # J2000 is defined as 1200 hrs UT on Jan 1st 2000 AD
    y, m, d = datetime2String_Num(UTC,'ymdx')
    if y == 2016 or y == 2020:
        daytomonth = DaystoMonthLY[m]
    else:
        daytomonth = DaystoMonthNoLY[m]
    days = d + daytomonth + DaystoYear[y]
    return days
    
def findLST(num_days, UTC, longde):
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

    dcHours = datetime2String_Num(UTC, 'hx')
    lstdeg = 100.46 + (0.985647 * num_days) + longde + (15 * dcHours)
    if lstdeg < 0:
        while lstdeg < 0:
            lstdeg += 360
    elif lstdeg > 360:
        while lstdeg > 360:
            lstdeg -= 360
    return lstdeg
    
def findHA(RA, LST):
    # Both RA and LST need to be in degrees 0 - 360.
    # Will output HA in degrees 0 - 360
    
    HA_tmp = LST - RA
    if HA_tmp < 0:
        while HA_tmp < 0:
            HA_tmp += 360
    elif HA_tmp > 360:
        while HA_tmp > 360:
            HA_tmp -= 360
    return HA_tmp
    
def findALT_AZMU(DEC_rads, HA_rads, LAT_rads):
    Alt = arcsin(sin(DEC_rads)*sin(LAT_rads)+cos(DEC_rads)*cos(LAT_rads)*cos(HA_rads))
    A = arccos(sin(DEC_rads)-sin(Alt)*sin(LAT*))/(cos(Alt)*cos(LAT_rads))
    if sin(HA_rads) < 0:
        Azmu = A
    else:
        Azmu = 2*pi - A
    # Now convert back to degrees the new values:
    Data = (Alt*(180/pi), Azmu*(180/pi))
    return Data

def downloadHTML(config, log, cwd, prefix='NA', **kwargs):
    ''' Function that downloads html text '''

    log('downloadHTML function called')
    html_data = urllib.request.urlopen(config['url'])
    log('HTML Downloaded from: ' + html)
    path = os.path.join(CurrentPath, prefix + '_html.tmp')
    with open(path,'wb') as filetmp:
        for line in html_data:
            filetmp.write(line)
    log('HTML Data Saved Locally in: ' + path)
    if kwargs.get('return_str', False):
        with open(path, 'r') as html_file:
            kstr = ''
            for line in html_file:
                # Make Large String of the HTML File
                kstr += line
        log('HTML data passed into super-string')
        return kstr
    elif kwargs.get('return_path', True):
        return path

def parseDataFile(htmldata, log):
    with open(os.path.join(cwd, source + '_ParseOutput.tmp'), 'w') as tmp_storage:
        nextline = 0
        nextlinego = 0
        newitem = 0
        newevents = 0
        actives = 0
        for line in htmldata:
            if newitem == 1:
                tmp_storage.write('\n\n ----NEW EVENT----\n')
                newevents += 1
            elif nextline == 1:
                strr = line[7:];
                if not strr == '= RIGHT\n':
                    strr = strr[1:]
                    tmp_storage.write(strr)
            elif nextlinego == 1:
                tmp_storage.write('LIVE!----------------\n')
                actives += 1
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
        log('    '+ str(newevents) + ' New Event(s) Found!')
        log('    ' + str(actives) + ' Active Event(s) Found!')
    with open(os.path.join(cwd, source + '_ParseOutput.tmp'), 'r') as data:
        log('--- PARSING INFORMATION ---')
        lines=data.readlines()
    events = []
    for i, line in enumerate(lines):
        if line == ' ----NEW EVENT----\n':
            if lines[i+1] == '\n':
                log.write('   Bad sector found, skipped: Line-'+str(i)+' = '+line)
            else:
                if lines[i+1]=='LIVE!----------------\n':
                    active = True;
                    skip = 1;
                else:
                    active = False;
                    skip = 0;
                dat = {}
                dat['active'] = active
                url = lines[i+1+skip]
                url = url[0:-1]
                starno = lines[i+2+skip]
                dat['starno'] = starno[0:-1]
                RA = lines[i+3+skip]
                dat['RA'] = RA[0:-1]
                DEC = lines[i+4+skip]
                dat['DEC'] = DEC[0:-1]
                tmaxhj = lines[i+5+skip]
                dat['tmaxhj'] = tmaxhj[0:-1]
                dat['tmaxhj_f'] = float(dat['tmaxhj'])
                tmaxut = lines[i+6+skip]
                dat['tmaxut'] = tmaxut[0:-1]
                tau = lines[i+7+skip]
                dat['tau'] = tau[0:-1]
                umin = lines[i+8+skip]
                dat['umin'] = umin[0:-1]
                amax = lines[i+9+skip]
                dat['amax'] = amax[0:-1]
                dmag = lines[i+10+skip]
                dat['dmag'] = dmag[0:-1]
                fbl = lines[i+11+skip]
                dat['fbl'] = fbl[0:-1]
                ibl = lines[i+12+skip]
                dat['ibl'] = ibl[0:-1]
                io = lines[i+13+skip]
                dat['io'] = io[0:-1]
                dat['io_f'] = float(dat['io'])
                dat['url'] = 'http://ogle.astrouw.edu.pl/ogle4/ews/'+url
                events.append(MicroEvent(dat))
    log('    --- PARSING END ---')
    return events