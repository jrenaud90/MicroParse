# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 21:08:13 2014
@author: jrenaud
"""

from HTMLParser import HTMLParser
import os,urllib2,datetime,sidereal
vers = '0.3.1'
def LogMaker(CurrentPath):
    logpath = CurrentPath + 'Output.log'
    log = open(logpath,'w')
    return log
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
        inputintoobject(datastore,csvform,log)
        pass
def inputintoobject(data,log):
    log.write('CSVfile made and header wrote\n')
    lines=data.readlines()
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
                event = microevent(active,url,starno,RA,DEC,tmaxj,tmaxut,tau,umin,amax,dmag,fbl,ibl,io)
				
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
class microevent:
	import os.path
	version = '0.1.5'
	versionDate = '8-9-2014'
	def __init__(self,a,u,f,s,r,d,tmj,tmu,umn,tu,am,dma,fbl,ibl,io):
		active = a
		html = u
		field = f
		starno = s
		ra = r
		dec = d
		t_max_hjd = tmj
		t_max_ut = tmu
		u_min = umn
		tau = tu
		a_max = am
		d_mag = dma
		f_bl = fbl
		i_bl = ibl
		i_o = io
	def changeValue(self,string,value)
		%Possible Input Strings:
		%	==active,html,field,starno,ra,dec,t_max_hjd,t_max_ut,tau,a_max,d_mag,f_bl,i_bl,i_o
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
	def parseVisibility(self,long,lat,UTC)
		%if condition:
			Visibility = 1
		%else:
		%Visibility = 0
		return Visibility
	def parseMinimumMag(self,MinMag)
		if self.i_o+self.d_mag > MinMag:
			MinMagTest = 0
		else:
			MinMagTest = 1
		return MinMagTest
	def parse(self,long,lat,utc,minmag,compact,filepath,printqur)
		parsepass = 0
		if (minmag == 'NA' and self.parseVisibility(long,lat,utc) == 1):
			parsepass = 1
		elif (self.parseMinimumMag(minmag) == 1 and self.parseVisibility(long,lat,utc) == 1):
			parsepass = 1
		if printqur == 1:
				self.printCSV(compact,filepath)
		return parsepass
	def printCSV(self,compact,filepath):
		if compact == 1:
			stringout = self.active+','+self.html+','+self.ra+','+self.dec+','+self.t_max_ut+','+self.tau+','+self.u_min+','+self.d_mag+','+self.i_bl+','+self.i_o+'\n'
		else:
			stringout = self.active+','+self.html+','+self.field+','+self.starno+','+self.ra+','+self.dec+','+self.t_max_hjd+','+self.t_max_ut+','+self.tau+','+self.u_min+','+self.a_max+','+self.d_mag+','+self.f_bl+','+self.i_bl+','+self.i_o+'\n'
		if s.path.isfile(filepath+'output.csv'):
			with open(filepath+'output.csv','a') as csv:
				csv.write(stringout)				
				pass
		else:
			with open(filepath+'output.csv','w') as csv:
				if compact == 1:
					csv.write('Active,HTML,RA(J2000),DEC(J2000),T_MAX(UT),tau,U_min,D_mag,f_bl,I_bl,I_o\n')
				else:
					csv.write('Active,HTML,Field,StarNo,RA(J2000),DEC(J2000),T_MAX(HJD),T_MAX(UT),tau,U_min,A_MAX,D_mag,f_bl,I_bl,I_o\n')
				csv.write(stringout)
				pass