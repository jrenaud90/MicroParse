# -*- coding: utf-8 -*-
from HTMLParser import HTMLParser
from numpy import sin,arcsin,cos,pi,arccos
from dateutil import tz
import os,urllib2,datetime,dropbox,webbrowser,Tkinter

class MuParse():
	def __init(self):
		self.version = '1.8.7p'

class MuParser():
	def __init__(self,website,**optional):
		self.version = '1.8.3p'
		self.date = '8-12-14'
		self.currentime = astroTimeObject(datetime.datetime.utcnow())
		## Optional Inputs
		if ('path' in optional):
			self.path = optional['path']
		elif ('filepath' in optional):
			self.path = optional['filepath']
		else:
			self.path = 'C:/MuParse/'+ 'Run_' + self.currentime.str_num('s2') + '/'
		###
		## Create Folder
		if not os.path.exists(self.path):
			os.makedirs(self.path)
		###
		## Create Log
		self.log = open(self.path+'Output.log','w')
		self.logwrite('---MuParse---\nWritten by Joe Renaud at George Mason University\nVersion: '+self.version+'\tDate: '+self.date+'\n')
		self.logwrite('MuParse Constructor Called\n')
		self.logwrite('Data to be recorded at '+self.path+'\n')
		###
		## Initial Website Analysis
		self.website = website
		self.websource = website
		if self.website == 'onlyparse':
			self.website = 0
			self.logwrite('No Website will be parsed, only data will be parsed\n')
		elif self.website == 'moa':
			self.website = 'https://it019909.massey.ac.nz/moa/alert2014/alert.html'
			self.logwrite('MOA data to be parsed.\nWeb address to be used: '+self.website+'\n')
		elif self.website == 'ogle':
			self.website = 'http://ogle.astrouw.edu.pl/ogle4/ews/ews.html'
			self.logwrite('OGLE4 data to be parsed.\nWeb address to be used: '+self.website+'\n')
	def logwrite(self,string):
		# New write command so that the log file continues to update as the
		# program runs, via the flush command.
		self.log.write(string)
		self.log.flush()
	def endparse(self):
		self.log.close()
	def download(self):
		if not self.website == 0:
			self.logwrite('Initializing...\n')
			self.logwrite('Opening: ' + self.website +'\n')
			HTMLData = urllib2.urlopen(self.website)
			self.logwrite('HTML Data Saved to Memory\n')
			with open(self.path+'html.tmp','w') as filetmp:
				for line in HTMLData:
					filetmp.write(line)
				pass
			self.logwrite('HTML Data Saved Locally\n')
			with open(self.path+'html.tmp','r') as htmltmp:
				self.logwrite('Reading '+self.path+'html.tmp as var: htmltmp.\n')
				self.htmlstring = ''
				for line in htmltmp:
					self.htmlstring = self.htmlstring + line
				pass
			self.logwrite('HTML data passed into super-string.\n')
			with open(self.path+'htmlparse.tmp','w') as htmldata:
				parser = MyHTMLParser()
				parser.htmldatastore(htmldata)
				parser.feed(self.htmlstring)
				self.logwrite('Superstring passed into parser object.\n')
				pass
		self.logwrite('download method complete.\n')
	def query(self):
		self.logwrite('query method called and running...\n')
		#Turn into GUI in the future
		d1 = raw_input('Do you want to use Default variables (y/n)? ')
		if d1 == 'n':
			self.logwrite('Non-Default valeus chosen by user\n')
			lonng = input('Observatory Longitude (def:-77.305325): ')
			lat = input('Observatory Latitude (def:38.828176): ')
			days = input('How many days from now do you want to parse to (def:30): ')
			prec = input('How many times a night do you want to check (def:9): ')
			prec = int((9*60)/prec)
			minALT = input('What is the lowest altitude you can observe at (def:20degrees): ')
			MinMag = input('What is the minimum magnitude you can observe (def:17): ')
			OnlyActive = raw_input('Only Active Events?(def:y): ')
			OnlyFuture = raw_input('Look at only future maximums?(def:y): ')
		else:
			self.logwrite('Default values chosen by user\n')
			prec = int(30) #minutes, I would keep this between 30 - 280
			lonng = -77.305325 #degrees East
			lat = 38.828176 #degrees North
			days = 30
			MinMag = 14 #Minimum Magnitude to detect
			minALT = 18 #Degrees above the horizon
			OnlyActive = 'y' #Look for only Active Events
			OnlyFuture = 'y' #Only look at future maximums in the events
		stringr = 'Values:\n\tObservatory Longitude: '+str(lonng)+'\
\n\tObservatory Latitude: '+str(lat)+'\n\tDays Out: '+str(days)+'\n\tPrecision: '+str(prec)+'\
\n\tLowest Altitude: '+str(minALT)+'\n\tMin Magnitude: '+str(MinMag)+'\n\tOnly Active: '+OnlyActive+'\
\n\tOnly Future Max: '+OnlyFuture+'\n'
		if OnlyActive == 'y':
			Act = 1
		else:
			Act = 0
		if OnlyFuture == 'y':
			OnlyFuture = 1
		else:
			OnlyFuture = 0
		self.logwrite(stringr)
		querydata = [prec,lonng,lat,days,MinMag,minALT,Act,OnlyFuture]
		return querydata
	def parse(self):
		querydata = self.query()
		precision = querydata[0]
		ObservLong = querydata[1]
		ObservLat = querydata[2]
		daysOut = querydata[3]
		MinMag = querydata[4]
		minALT = querydata[5]
		OnlyActive = querydata[6]
		OnlyFuture = querydata[7]
		compactPrintout = 'n'
		self.logwrite('Parse Method is now running...\n')
		self.logwrite('CompactPrintout: ' + compactPrintout+'\n')
		with open(self.path+'htmlparse.tmp','r') as htmldata:
			self.logwrite('Data found!\n')
			with open(self.path + 'ParseOutput.tmp','w') as datastore:
				self.ParseDataFile(htmldata,datastore)
				pass
			pass
		with open(self.path + 'ParseOutput.tmp','r') as datastore:
			events = self.inputintoobject(datastore)
			self.logwrite('Events Found\n')
			pass
		times = self.dateFinder('y',daysOut,precision)
		self.logwrite('Times Found\n')
		self.logwrite('events: ' + str(len(events))+'\n')
		self.logwrite('times: ' + str(len(times))+'\n')
		self.logwrite('Running through events and times\n')
		timerr = len(times)
		print '25% Complete'
		self.logwrite('All major calculations complete.\nParsing over times and events: 25% complete.\n')
		dt = float(float((100-25))/timerr)
		perc = float(25)
		pold = 25
		for time in times:
			perc = perc + dt
			pnew = int(perc)
			if pnew != pold:
				print str(pnew) + '% Complete'
				pold = pnew
			for event in events:
				data = event.parse(ObservLong,ObservLat,time,MinMag,minALT,OnlyActive,OnlyFuture)
				if data[0]:
					event.print2CSV(compactPrintout,self.path,time,data[1],data[2])
		self.logwrite('Parser Finished!\n')
		print '100% Complete'
		self.endparse()
	def dateFinder(self,NowQ,days,precision):
		self.logwrite('dateFinder method called.\n')
		#days - out from now
		#precision in minutes
		starthourUTC = '23:00'
		endhourUTC = '04:30'
		shour = int(starthourUTC[0:2])
		smin = int(starthourUTC[3:len(starthourUTC)])
		ehour = int(endhourUTC[0:2])
		emin = int(endhourUTC[3:len(endhourUTC)])
		self.logwrite('Start UTC: ' + starthourUTC + '\n')
		self.logwrite('End UTC: ' + endhourUTC + '\n')
		daysinmonthsNolp = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
		daysinmonthslp = daysinmonthsNolp
		daysinmonthslp[2] = 29
		#Note, code does not account for leap years at this stage.
		if NowQ == 'y':
			ymd = self.currentime.str_num('donly')
			syear = ymd[0]
			smonth = ymd[1]
			if shour > 10:
				sday = ymd[2]
			else:
				sday = ymd[2]
			hmns = self.currentime.str_num('tonly')
			shour = hmns[0]
			if shour >= 0 and shour <= 4:
				if sday == 1:
					if smonth == 1:
						syear = syear -1
						smonth = 12
					else:
						smonth = smonth - 1
					if syear == 2016 or syear == 2020:
						sday = daysinmonthslp[smonth]
					else:
						sday = daysinmonthsNolp[smonth]
				else:
					sday = sday - 1
			if ehour > 10:
				if ehour >= shour:
					if emin >= smin:
						eday = sday
					else:
						eday = sday + 1
				else:
					eday = sday + 1
			else:
				eday = sday + 1
			thour = shour
			tmin = smin
			tday = sday
			tmonth = smonth
			tyear = syear
			UTCtimes = []
			for i in range(1,days):
				thour = shour
				tmin = smin
				if tday > daysinmonthsNolp[tmonth]:
					tday = tday - daysinmonthsNolp[tmonth]
					tmonth +=1
					if tmonth > 12:
						tmonth = 1
						tyear += 1
				while thour < ehour or tmin < emin or tday < eday:
					UTCtimes.append(datetime.datetime(tyear,tmonth,tday,thour,tmin))
					tmin = tmin+precision
					while tmin >= 60:
						thour +=1
						tmin -= 60
					while thour >= 24:
						tday +=1
						thour -= 24
				tday = tday + 1
		else:
			print 'Sorry, this feature is not yet implemented.'
		self.logwrite('Times are output.\n')
		return UTCtimes
	def ParseDataFile(self,htmldata,datastore):
		self.logwrite('ParseDataFile Method Called \n')
		nextline = 0
		nextlinego = 0
		newitem = 0
		newevents = 0
		actives = 0
		if self.websource == 'ogle':
			self.logwrite('OGLE Called in ParseDataFile Method\n')
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
					datastore.write('LIVE!\n')
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
		elif self.websource == 'moa':
			print 'Not Yet Implemented'
		datastore.flush()
		self.logwrite('--- '+ str(newevents)+ ' New Event(s) Found!\n')
		self.logwrite('--- ' + str(actives) + ' Active Event(s) Found!\n')
	def inputintoobject(self,data):
		self.logwrite('inputintoobject method called\n')
		lines=data.readlines()
		events = []
		if self.websource == 'ogle':
			self.logwrite('OGLE-type in use.\n')
			for i, line in enumerate(lines):
				if line == ' ----NEW EVENT----\n':
					if lines[i+1] == '\n':
						self.logwrite('bad sector found, skipped. \n')
					else:
						if lines[i+1]=='LIVE!\n':
							active = '1';
							skip = 1;
						else:
							active = '0';
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
						ider = url
						url = 'http://ogle.astrouw.edu.pl/ogle4/ews/'+url
						events.append(microevent(ider,active,url,starno,RA,DEC,tmaxhj,tmaxut,tau,umin,amax,dmag,fbl,ibl,io))
		elif self.websource == 'moa':
			print 'not implemented yet'
		self.logwrite('events to be output.\n')
		return events

class microevent:
	version = '0.5.2p'
	versionDate = '8-15-2014'
	def __init__(self,ider,a,u,s,r,d,tmj,tmu,tu,umn,am,dma,fbl,ibl,io):
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
		self.gmuid = 'GM-'+ider
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
		# Methods based upon the great website:
		# http://www.stargazing.net/kepler/altaz.html accesed 8/2014
		# Please cite the above in any publications
		d = UTC.days2J2000()
		LST = self.LST_finder(d,UTC,lonng)
		HA = self.HA_finder(LST)
		AltAz = self.AltAzmu_finder(HA,lat)
		alt = AltAz[0]
		azmu = AltAz[1]
		if alt < minALT:
			IsVis = False
		else:
			IsVis = True
		VisibData = [IsVis,alt,azmu]
		return VisibData
	def parseMinimumMag(self,MinMag):
		if float(self.i_o)< MinMag:
			MinMagTest = True
		else:
			MinMagTest = False
		return MinMagTest
	def parseFuture(self,futureDate):
		if (float(self.t_max_hjd)-futureDate) > 0:
			Future = True
		else:
			Future = False
		return Future
	def parse(self,lonng,lat,utc,minmag,minALT,OnlyActive,OnlyFuture):
		#Long and Lat must be in decimal degrees eg: 23.210012
		#UTC must be a datetime object.
		#minmag should be in conventional units.
		#minALT should be in degrees 0-90
		#OnlyActive and OnlyFuture should be 1 for yes, 0 for no
		UTC = astroTimeObject(utc)
		if OnlyFuture == 1:
			currentJD = UTC.days2J2000()
			FutureQuery = self.parseFuture(currentJD)
		else:
			FutureQuery = True
		VisibData = self.parseVisibility(lonng,lat,UTC,minALT)
		if int(self.active) == OnlyActive and VisibData[0] and self.parseMinimumMag(minmag) and FutureQuery:
			parsedata = VisibData
		else:
			parsedata = [False,0,0]
		return parsedata
	def print2CSV(self,compact,filepath,time,alt,azmu):
		time = astroTimeObject(time)
		if compact == 'y':
			stringout = self.gmuid+','+self.active+','+time.str_num('s_estedt')+','+str(alt)+','+str(azmu)+','+self.html+','+self.ra+','+self.dec+','+self.t_max_ut+','+self.tau+','+self.u_min+','+self.d_mag+','+self.i_bl+','+self.i_o+'\n'
		else:
			stringout = self.gmuid+','+self.active+','+time.str_num('s_estedt')+','+str(alt)+','+str(azmu)+','+self.html+','+self.starno+','+self.ra+','+self.dec+','+self.t_max_hjd+','+self.t_max_ut+','+self.tau+','+self.u_min+','+self.a_max+','+self.d_mag+','+self.f_bl+','+self.i_bl+','+self.i_o+'\n'
		if os.path.isfile(filepath+'output.csv'):
			with open(filepath+'output.csv','a') as csv:
				csv.write(stringout)
				pass
		else:
			with open(filepath+'output.csv','w') as csv:
				if compact == 'y':
					csv.write('GMU_ID,Active,Date-Time(USEAST),Alt,Azmu,HTML,RA(J2000),DEC(J2000),T_MAX(UT),tau,U_min,D_mag,f_bl,I_bl,I_o\n')
					csv.write(stringout)
				else:
					csv.write('GMU_ID,Active,Date-Time(USEAST),Alt,Azmu,HTML,StarNo,RA(J2000),DEC(J2000),T_MAX(HJD),T_MAX(UT),tau,U_min,A_MAX,D_mag,f_bl,I_bl,I_o\n')
					csv.write(stringout)
				pass
	def DECtoDeg(self,radQ,**DEC):
		if ('DEC' in DEC):
			string = DEC
		else:
			string = self.dec
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
	def RAtoHours_Deg(self,ConvrtDegQ,**RA):
		if ('RA' in RA):
			string = RA['RA']
		else:
			string = self.ra
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
	def AltAzmu_finder(self,HA,LAT,**RA_DEC):
		if ('RA' in RA_DEC):
			RA = RA_DEC['RA']
		else:
			RA = self.ra
		if ('DEC' in RA_DEC):
			DEC = RA_DEC['DEC']
		else:
			DEC = self.dec
		RA = self.RAtoHours_Deg('y')
		DEC = self.DECtoDeg('n')
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
	def LST_finder(self,d,Ut,lonng):
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
		dcHours = Ut.str_num('hx')
		lstdeg = 100.46+(0.985647*d)+lonng+(15*dcHours)
		if lstdeg < 0:
			while lstdeg < 0:
				lstdeg = lstdeg + 360
		elif lstdeg > 360:
			while lstdeg > 360:
				lstdeg = lstdeg - 360
		lst = lstdeg
		return lst
	def HA_finder(self,LST,**RA):
		#Both RA and LST need to be in degrees 0 - 360.
		#Will output HA in degrees 0 - 360
		if ('RA' in RA):
			RA = RA['RA']
		else:
			RA = self.RAtoHours_Deg('y')
		HAtmp = LST - RA
		if HAtmp < 0:
			while HAtmp < 0:
				HAtmp = HAtmp + 360
		elif HAtmp > 360:
			while HAtmp > 360:
				HAtmp = HAtmp - 360
		HA = HAtmp
		return HA

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
class astroTimeObject():
	def __init__(self,UTCDateTimeObject):
		self.utc=UTCDateTimeObject
		from_zone = tz.gettz('UTC')
		to_zone = tz.gettz('America/New_York')
		UTC = self.utc.replace(tzinfo=from_zone)
		self.edst = UTC.astimezone(to_zone)
	def str_num(self,outputType):
		y = self.utc.year
		m = self.utc.month
		d = self.utc.day
		h = self.utc.hour
		mn = self.utc.minute
		s = self.utc.second
		if outputType == 's':
			output = str(m)+'-'+str(d)+'-'+str(y)+' '+str(h)+':'+str(mn)+':'+str(s)
		elif outputType =='s_estedt':
			output = str(self.edst.month)+'-'+str(self.edst.day)+'-'+str(self.edst.year)+' '+str(self.edst.hour)+':'+str(self.edst.minute)+':'+str(self.edst.second)
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
		elif outputType == 's2':
			if m <10:
				m = '0' + str(m)
			else:
				m = str(m)
			if d <10:
				d = '0' + str(d)
			else:
				d = str(d)
			if h <10:
				h = '0' + str(h)
			else:
				h = str(h)
			if mn <10:
				mn = '0' + str(mn)
			else:
				mn = str(mn)
			if s <10:
				s = '0' + str(s)
			else:
				s = str(s)
			output = str(m)+str(d)+str(y)+'-'+str(h)+str(mn)+str(s)
		return output
	def days2J2000(self):
		#input is a datetime object in UTC
		#J2000 is defined as 1200 hrs UT on Jan 1st 2000 AD
		##Days to beginning of year
		DaystoYear = {1998:-731.5,1999:-366.5,2000:-1.5,2001:364.5,2002:729.5,2003:1094.5,2004:1459.5,2005:1825.5,2006:2190.5,2007:2555.5,2008:2920.5,2009:3286.5,2010:3651.5,2011:4016.5,2012:4381.5,2013:4747.5,2014:5112.5,2015:5477.5,2016:5842.5,2017:6208.5,2018:6573.5,2019:6938.5,2020:7303.5,2021:7669.5}
		##Days to beginning of month:
		DaystoMonthLY = {1:0,2:31,3:60,4:91,5:121,6:152,7:182,8:213,9:244,10:274,11:305,12:335}
		DaystoMonthNoLY = {1:0,2:31,3:59,4:90,5:120,6:151,7:181,8:212,9:243,10:273,11:304,12:334}
		out = self.str_num('ymdx')
		d = out[2]
		m = out[1]
		y = out[0]
		if y == 2016 or y == 2020:
			daytomonth = DaystoMonthLY[m]
		else:
			daytomonth = DaystoMonthNoLY[m]
		days = d + daytomonth + DaystoYear[y]
		return days
class MyHTMLParser(HTMLParser):
	def htmldatastore(self,htmldata):
		self.htmldataholder = htmldata
	def handle_data(self, data):
		if len(data) > 1:
			self.htmldataholder.write('::DATA: ' + data + '\n')
	def handle_starttag(self, tag, attrs):
		self.htmldataholder.write('Item: \n')
		self.htmldataholder.write('::TAG: ' + tag + '\n')
		for attr in attrs:
			if len(attr)<2:
				self.htmldataholder.write('\t' + attr + '\n')
			else:
				st1 = attr[0]
				st2 = attr[1]
				self.htmldataholder.write('\t' + st1 + ' = ' + st2 + '\n')

class DropboxDB():
	#dependencies: import dropbox (install sdk from their site) and webbrowser

	def __init__(self,**additional):
		self.localpath = 'C:/MuParse/'
		if ('log' in additional):
			self.logwrite = additional['log']
		else:
			my = MuParser('ogle')
			self.logwrite = my.logwrite
		self.version = '0.1.0n'
		self.appkey = '2zrff7pqdxg9mbc'
		self.appsecret = 'mixs1tiavqpqw5v'
		self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(self.appkey, self.appsecret)
		self.authorize_url()
	def authorize_url(self):
		url = self.flow.start()
		webbrowser.open(url, new=1, autoraise=True)
		code = raw_input("Enter the authorization code here: ").strip()
		access_token, self.user_id = self.flow.finish(code)
		self.client = dropbox.client.DropboxClient(access_token)
	def upload(self,filepath,filename,rev):
		filename = '/gexobase/'+filename
		with open(filepath,'rb') as f:
			response = self.client.put_file(filename, f,overwrite=True)
			self.logwrite('uploaded '+filename+', response:\n')
			for item in response:
				self.logwrite('\t'+str(item) + ':'+str(response[item]))
			pass
	def download(self,filedownloadpath,filename):
		filename = '/gexobase/'+filename
		f, metadata = self.client.get_file_and_metadata(filename)
		self.logwrite(filename+' downloaded to: ' + filedownloadpath+'\n')
		with open(filedownloadpath,'wb') as out:
			out.write(f.read())
			out.close()
			self.logwrite(filename+' downloaded to: ' + filedownloadpath+'\n')
			self.logwrite('Metadata: \n')
			for item in metadata:
				self.logwrite('\t'+str(item) + ':'+str(metadata[item]))
			revision = metadata['revision']
			pass
			return revision
	def CreateTBL(self,localpath,filename,tablename):
		with open(localpath + filename +'.csv','w') as localfile:
			localfile.write(tablename+'\n')
			pass
		self.upload(localpath,filename+'.csv',1)
	def AppendLineTBL(self,line,tbl,up,new):
		if new == True:
			self.download(self.localpath,tbl+'.csv')
		with open(self.localpath+tbl+'.csv','a') as filetmp:
			filetmp.write(line+'\n')
			pass
		if up == True:
			self.upload(self.localpath,tbl+'.csv')
	def ReadTBL(self,tbl,new):
		if new == True:
			self.download(self.localpath,tbl+'.csv')

	def parse_GMUID_DB(self):
		filename = 'GMUID.csv'
		filelocalpath = self.localpath + 'temp/'
		if not os.path.exists(filelocalpath):
			os.makedirs(filelocalpath)
		filepath = filelocalpath + filename
		rev = self.download(filepath,filename)
		#rev = rev + 1
		print rev
		with open(filepath,'a') as DBfile:
			DBfile.write('hello,')
			pass
		self.upload(filepath,filename,rev)
class Table():
	def __init__(self,table,**othervars):
		self.version = '0.2.0'
		if 'header_row' in othervars:
			self.headrow = othervars['header_row']
		else:
			self.headrow = 0
		if 'firstdata_row' in othervars:
			self.datarow = othervars['firstdata_row']
		else:
			self.datarow = 1
		if 'delim' in othervars:
			self.delim = othervars['delim']
		else:
			self.delim = ','
		self.pl = 0
		self.inputparse(table)
		self.findHeaders()
		self.findData()
	def inputparse(self,inpt):
		if type(inpt)==type('test'):
			if os.path.exists(inpt):
				self.LoadfromFile(inpt)
			elif os.access(os.path.dirname(inpt), os.W_OK):
				raise Exception('No File Found at Path')
			else:
				self.LoadfromStr(inpt)
		elif type(inpt)==type(['test','test']):
			self.LoadfromList(inpt)
	def LoadfromFile(self,filepath):
		with open(filepath,'r') as filetmp:
			rows = list(filetmp)
			pass
		rownew = []
		for i,item in enumerate(rows):
			if item[-1]=='\n':
				rownew.append(item[0:-1])
			else:
				rownew.append(item)
		self.rows = rownew
	def LoadfromStr(self,string):
		newlines = self.findstr(string,'\n')
		rows = []
		for i in newlines:
			if i == 0:
				rows.append(string[0:newlines[0]])
			elif i == len(newlines):
				rows.append(string[newlines[i]+1:-1])
			else:
				rows.append(string[newlines[i]+1:newlines[i+1]])
		rownew = []
		for i,item in enumerate(rows):
			if item[-1]=='\n':
				rownew.append(item[0:-1])
			else:
				rownew.append(item)
		self.rows = rownew
	def LoadfromList(self,listr):
		rownew = []
		for i,item in enumerate(listr):
			print listr
			print item
			if item[-1]=='\n':
				rownew.append(item[0:-1])
			else:
				rownew.append(item)
		self.rows = rownew
	#### String and Row Tools ####
	def findstr(self,s,c):
		locations = []
		for i,char in enumerate(s):
			if char == c:
				locations.append(i)
		return locations
	def findRowValues(self,Row):
		Values = []
		DelimLocal = self.findstr(Row,self.delim)
		l2 = len(DelimLocal)
		for i,local in enumerate(DelimLocal):
			if i == 0:
				tmp = Row[0:local]
			else:
				tmp = Row[DelimLocal[(i-1)]+1:local]
			if not tmp:
				tmp = None
			Values.append(tmp)
		if Row[-1]=='\n':
			tmp = Row[DelimLocal[l2-1]+1:-1]
		else:
			tmp = Row[DelimLocal[l2-1]+1:len(Row)]
		if not tmp:
			tmp = None
		Values.append(tmp)
		return Values
	#### Table Tools ####
	def findHeaders(self):
		self.headers = self.findRowValues(self.rows[self.headrow])
		self.headers.append('Tbl_ID')
		self.datafieldNum = len(self.headers)
		for item in self.headers:
			if len(str(item))>self.pl:
				self.pl = len(item)
	def findData(self):
		data = []
		for j,row in enumerate(self.rows[self.headrow+1:len(self.rows)]):
			datainrow = self.findRowValues(row)
			rowdictionary = {}
			for i,value in enumerate(datainrow):
				rowdictionary[self.headers[i]] = value
				if len(str(value)) > self.pl:
					self.pl = len(value)
			rowdictionary['Tbl_ID']=j
			data.append(rowdictionary)
		self.data = data
	def searchhead(self,headerString):
		out = []
		if type(headerString)==type(['test','test']):
			for i,dataitem in enumerate(self.data):
				item = []
				for header in headerString:
					item.append(dataitem[header])
				item.append(dataitem['Tbl_ID'])
				out.append(item)
		elif type(headerString) == type('test'):
			for i,dataitem in enumerate(self.data):
				item = []
				item.append(dataitem[headerString])
				item.append(dataitem['Tbl_ID'])
				out.append(item)
		else:
			raise Exception('Invalid input type')
		return out
	def searchdata(self,**keyword):
		#For numbers, you can enter a list [value,pluserror,minuserror], [value,error]
		#or just the value and no list, in which case error will be treated as 0
		results = []
		for key in keyword:
			if not(key in self.headers):
				raise Exception('Keyword not found in headers')
			else:
				for data in self.data:
					if type(keyword[key])==type('string'):
						if data[key] == keyword[key]:
							if not data['Tbl_ID'] in results:
								results.append(data['Tbl_ID'])
					elif type(keyword[key])==type(1) or type(keyword[key])==type(1.0):
						if float(data[key]) == float(keyword[key]):
							if not (data['Tbl_ID'] in results):
								results.append(data['Tbl_ID'])
					elif type(keyword[key])==type([1,1]):
						values = keyword[key]
						if len(values) == 2:
							value = values[0]
							valueplserror = values[1]
							valueminserror = valueplserror
						elif len(values) == 3:
							value = values [0]
							valueplserror = values[1]
							valueminserror = values[2]
						else:
							raise Exception('Too many or Too Few list items')
						datavalue = data[key]
						diff = float(datavalue) - float(value)
						if diff < valueplserror and diff > (-1*valueminserror):
							if not data['Tbl_ID'] in results:
								results.append(data['Tbl_ID'])
		result = []
		for ID in results:
			result.append(self.data[ID])
		return result
	def disp(self):
		str1 = ''
		for i,item in enumerate(self.headers):
			if i == len(self.headers):
				str1 = str1 + str(item)
			else:
				spnum = self.pl+3 - (len(str(item))+2)
				str1 = str1 + str(item)+':' + ' '*spnum
		print str1 + '\n'
		for i,item in enumerate(self.data):
			str2 = ''
			for j in range(0,self.datafieldNum):
				if j == self.datafieldNum:
					str2 = str2 + str(item[self.headers[j]])
				else:
					spnum = self.pl+3 - (len(str(item[self.headers[j]]))+1)
					str2 = str2 + str(item[self.headers[j]]) + ' '*spnum
			print str2 + '\n'



