# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 21:08:13 2014
Ver 0.1
@author: jrenaud
"""

from HTMLParser import HTMLParser
import os,inspect,urllib2,datetime,shutil
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
   # def handle_data(self, data):
        #if len(data) > 1:
            #htmldata.write('::DATA: ' + data + '\n')
    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            for attr in attrs:
                if len(attr)<2:
                    htmldata.write(attr + '\n')
                else:
                    st1 = attr[0]
                    st2 = attr[1]
                    htmldata.write(st1 + ' = ' + st2 + '\n')
def DownloadHTMLtext(html,log):
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
FolderPath = 'C:/MicroLensParse/'
if not os.path.exists(FolderPath):
    os.makedirs(FolderPath)
CurrentPath = FolderPath + 'Run_' + UTC2str(CurrentUTC()) + '/'
os.makedirs(CurrentPath)
logpath = CurrentPath + 'Output.log'
with open(logpath,'w') as log:
    log.write('Exoplanet Micro Lens Parsing Log\nVersion 0.1, by Joe Renaud\n')
    Website = 'http://ogle.astrouw.edu.pl/ogle4/ews/ews.html'
    log.write('Initializing...\n')
    log.write('Opening: ' + Website +'\n')
    kstr = DownloadHTMLtext(Website,log)
    with open(CurrentPath+'htmlparse.tmp','w') as htmldata:
        parser = MyHTMLParser()
        parser.feed(kstr)
        pass
        
    
    
    
    pass