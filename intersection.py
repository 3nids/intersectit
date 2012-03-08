"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Process class
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import math

import numpy as np
from numpy import linalg as la



class intersection:
	def __init__(self,initPoint,xyrpi):
		self.initPoint = initPoint
		self.xyrpi = xyrpi
		self.nc = len(xyrpi)
		
	def getSolution(self):
		if self.nc<2:
			raise NameError(QApplication.translate("Triangulation", "Less than 2 circles were find within threshold.", None, QApplication.UnicodeUTF8))
		elif self.nc==2:
			pts = self.twoCirclesIntersect()
			d1 = pts[0].sqrDist(self.initPoint)
			d2 = pts[1].sqrDist(self.initPoint)
			print d1
			print d2
			if d1<d2:
				return pts[0]
			else:
				return pts[1]
		else:
			return self.leastSquares()
			
	def leastSquares(self):
		threshold = .0005 # in meters
		# initial parameters
		x0  = np.array( [ self.initPoint.x() , self.initPoint.y() ] )
		print "Initial: %f,%f" % (x0[0],x0[1])
		dx = [2*threshold,2*threshold]
		while min(dx)>threshold:
			# jacobian for parameters
			A   = np.array( [ [2*self.initPoint.x()-2*c[0].x(),2*self.initPoint.y()-2*c[0].y()] for c in self.xyrpi ] )
			# jacobian for observations
			B   = np.diag( [ -2*c[1] for c in self.xyrpi ] )
			# stochastic model
			Qll = np.diag([math.pow(c[2],2)   for c in self.xyrpi ])
			Pm  = np.dot( B , np.dot(Qll,B.T) )
			P   = la.inv( Pm )
			# misclosure
			w   = np.array([ math.pow(x0[0]-c[0].x(),2) + math.pow(x0[1]-c[0].y(),2) - math.pow(c[1],2) for c in self.xyrpi ])
			# normal matrix
			N = np.dot( A.T , np.dot(P,A) )
			u = np.dot( A.T , np.dot(P,w) )
			# QR decomposition
			q,r = la.qr(N)
			p   = np.dot(q.T,u)
			dx  = np.dot(la.inv(r),p)
			x0 -= dx
			print "Correction: %f,%f" % (dx[0],dx[1])
		print "Solution: %f,%f" % (x0[0],x0[1])
		Qxx = la.inv(N)
		p1 = math.sqrt(Qxx[0][0])
		p2 = math.sqrt(Qxx[1][1])
		print p1,p2
		return QgsPoint(x0[0],x0[1])
						
	def twoCirclesIntersect(self):
		# see http://www.mathpages.com/home/kmath396/kmath396.htm
		[pt1,r1,p1,i1] = self.xyrpi[0]
		[pt2,r2,p2,i2] = self.xyrpi[1]
		x1 = pt1.x()
		y1 = pt1.y()
		x2 = pt2.x()
		y2 = pt2.y()
		d = math.sqrt( pt1.sqrDist(pt2) )
		if d<math.fabs(r1-r2):
			# circle is within the other
			return
		if d>r1+r2:
			print "Triangulation :: circles are separate, scaling radius to get intersection"
			s = d/(r1+r2)
			r1*=s
			r2*=s
		a = math.sqrt( (d+r1+r2) * (d+r1-r2) * (d-r1+r2) * (-d+r1+r2) ) / 4
		xlt = (x1+x2)/2.0 - (x1-x2)*(r1*r1-r2*r2)/(2.0*d*d)
		ylt = (y1+y2)/2.0 - (y1-y2)*(r1*r1-r2*r2)/(2.0*d*d)
		xrt = 2.0*(y1-y2)*a/(d*d)
		yrt = 2.0*(x1-x2)*a/(d*d)
		xa = xlt + xrt
		ya = ylt - yrt
		xb = xlt - xrt
		yb = ylt + yrt
		return [QgsPoint(xa,ya),QgsPoint(xb,yb)]
		
		
		
