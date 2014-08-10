class microevent:
	import os.path
	version = '0.1.0'
	versionDate = '8-9-2014'
	def __init__(self,active,html,field,starno,ra,dec,t_max_hjd,t_max_ut,tau,a_max,d_mag,f_bl,i_bl,i_o):
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
			stringout = self.active+','+self.html+','+self.ra+','+self.dec+','+self.t_max_ut+','+self.tau+','+self.d_mag+','+self.f_bl+','+self.i_o+'\n'
		else:
			stringout = self.active+','+self.html+','+self.field+','+self.starno+','+self.ra+','+self.dec+','+self.t_max_hjd+','+self.t_max_ut+','+self.tau+','+self.a_max+','+self.d_mag+','+self.f_bl+','+self.i_bl+','+self.i_o+'\n'
		if s.path.isfile(filepath+'output.csv'):
			with open(filepath+'output.csv','a') as csv:
				csv.write(stringout)				
				pass
		else:
			with open(filepath+'output.csv','w') as csv:
				csv.write(stringout)
				pass