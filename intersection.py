"""
IntersectIt QGIS plugin
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
	def __init__(self,initPoint,observations):
		self.initPoint = initPoint
		self.observations = observations
		self.nc = len(observations)
		
	def getSolution(self):
		if self.nc<2:
			raise NameError(QApplication.translate("IntersectIt", "Less than 2 observations were found within threshold.", None, QApplication.UnicodeUTF8))
		elif self.nc==2:
			pts = self.twoCirclesIntersect()
			d1 = pts[0].sqrDist(self.initPoint)
			d2 = pts[1].sqrDist(self.initPoint)
			if d1<d2:
				return pts[0]
			else:
				return pts[1]
		else:
			return self.leastSquares()
			
	def leastSquares(self):
		# distance equation: (x - xc)^2 + (y-yc)^2 - l^2 = 0 (obs: r, param: xc,yc, fixed: x,y)
		threshold = .0005 # in meters
		# initial parameters
		x0  = np.array( [ self.initPoint.x() , self.initPoint.y() ] )
		print "Initial: %f,%f" % (x0[0],x0[1])
		dx = [2*threshold,2*threshold]
		while max(np.abs(dx))>threshold:
			# init matrices
			A   = []
			B   = []
			Qll = []
			w   = []
			for i,obs in enumerate(self.observations):
				if obs["type"] == "distance":
					# jacobian for parameters
					A.append( [2*x0[0]-2*obs["x"] , 2*x0[1]-2*obs["y"]] )
					# jacobian for observations
					B.append(-2*obs["measure"])
					# stochastic model
					Qll.append( math.pow(obs["precision"],2))
					# misclosure
					w.append( math.pow(x0[0]-obs["x"],2) + math.pow(x0[1]-obs["y"],2) - math.pow(obs["measure"],2) )
					
			# generate matrices
			A   = np.array( A   )
			B   = np.diag(  B   )
			Qll = np.diag(  Qll )
			w   = np.array(  w   )
			
			# weight matrix
			Pm  = np.dot( B , np.dot(Qll,B.T) )
			P   = la.inv( Pm )
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
		x1 = self.observations[0]["x"]
		y1 = self.observations[0]["y"]
		r1 = self.observations[0]["measure"]
		x2 = self.observations[1]["x"]
		y2 = self.observations[1]["y"]
		r2 = self.observations[1]["measure"]
		
		d = math.sqrt( math.pow(x1-x2,2) + math.pow(y1-y2,2) )
		if d<math.fabs(r1-r2):
			# circle is within the other
			return
		if d>r1+r2:
			print "IntersectIt :: circles are separate, scaling radius to get intersection"
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
		
		
		
