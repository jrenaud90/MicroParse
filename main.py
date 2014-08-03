# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 21:08:13 2014
Ver 0.1
@author: jrenaud
"""

from HTMLParser import HTMLParser
import os,inspect,urllib2,datetime,shutil
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
    log.write('Exoplanet Micro Lens Parsing Log\nVersion 0.1, by Joe Renaud\n')
    Website = 'http://ogle.astrouw.edu.pl/ogle4/ews/ews.html'
    log.write('Initializing...\n')
    log.write('Opening: ' + Website +'\n')
    kstr = DownloadHTMLtext(Website,log,CurrentPath)
    global htmldata
    with open(CurrentPath+'htmlparse.tmp','w') as htmldata:
        parser = MyHTMLParser()
        parser.feed(kstr)
        pass
    OnlyParse(CurrentPath)
def OnlyParse(Path):
    try:
        log
    except NameError:
        log = LogMaker(Path)
        log.write('Exoplanet Micro Lens Parsing Log\nVersion 0.1, by Joe Renaud\n')
        log.write('Log did not exist.')
        log.write('Checking for data at ' + Path)
    else:
        log.write('OnlyParse function is now running...\n')
    try:
        global htmldata
        global datastore
        with open(Path+'htmlparse.tmp','r') as htmldata:
            log.write('Data found!')
            with open(Path + 'ParseOutput.tmp','w') as datastore:
                ParseDataFile(htmldata,datastore,log)
                pass
            pass
    except:
        log.write('Data not found :-(')
        log.write('Error thrown: Counsel-- No File Found at ' + Path)
        print "No File Found at " + Path
def csvsaver(path,log):
    
    with open(path+'csvformat.csv','w') as csvform:
        csvform.write('Active,Field,StarNo,RA(J2000),DEC(J2000),T_MAX(HJD),T_MAX(UT),tau,U_min,A_MAX,D_mag,f_bl,I_bl,I_o')
        pass
    
def ParseDataFile(htmldata,datastore,log):
    nextline = 0;
    nextlinego = 0;
    newitem = 0
    for line in htmldata:
        if newitem == 1:
            datastore.write('\n\n ----NEW EVENT----\n')
            log.write('---New Event Found!')
        elif nextline ==1:
            strr = line[7:];
            if not strr == '= RIGHT\n':
                strr = strr[1:]
                datastore.write(strr)
        elif nextlinego == 1:
            datastore.write('LIVE!----------------\n')
            log.write('---Active Event Found!')
        
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
    Full = y+m+d+'-'+hr+mn+sc
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