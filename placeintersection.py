"""
IntersectIt QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

mapTools
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import math
import numpy as np
from numpy import linalg as la

from intersectitsettings import IntersectItSettings
from memorylayers import MemoryLayers
from placedimension import PlaceDimension

from ui.ui_place_distance import Ui_place_distance
from ui.ui_LSreport import Ui_LSreport

class placeIntersectionOnMap(QgsMapToolEmitPoint):
	def __init__(self, iface, rubber):
		self.iface = iface
		self.canvas = iface.mapCanvas()
		self.rubber = rubber
		self.lineLayer = MemoryLayers(iface).lineLayer
		self.pointLayer = MemoryLayers(iface).pointLayer
		QgsMapToolEmitPoint.__init__(self, self.canvas)
		self.settings = IntersectItSettings()
		self.tolerance = self.settings.value("intersecSelectTolerance")
		units = self.settings.value("intersecSelectUnits")
		if units == "pixels": self.tolerance *= self.canvas.mapUnitsPerPixel()
		

	def canvasMoveEvent(self, mouseEvent):
		# put the observations within tolerance in the rubber band
		self.rubber.reset()
		point = self.toMapCoordinates( mouseEvent.pos() )
		featReq = QgsFeatureRequest()
		featReq.setFilterRect( self.getBox(point) )
		f = QgsFeature()
		iter = self.lineLayer().getFeatures(featReq)
		while (iter.nextFeature(f)):
			self.rubber.addGeometry( f.geometry() , None )

	def canvasPressEvent(self, mouseEvent):
		self.rubber.reset()
		observations = []
		point = self.toMapCoordinates( mouseEvent.pos() )
		featReq = QgsFeatureRequest()
		featReq.setFilterRect( self.getBox(point) )
		f = QgsFeature()
		iter = self.lineLayer().getFeatures(featReq)
		while (iter.nextFeature(f)):
			observations.append({	"type": f.attribute("type").toString(),
									"x": f.attribute("x").toDouble()[0],
									"y": f.attribute("y").toDouble()[0],
									"measure": f.attribute("measure").toDouble()[0],
									"precision": f.attribute("precision").toDouble()[0] })
		self.doIntersection(point, observations)

	def getBox(self,point):
		return QgsRectangle(point.x()-self.tolerance,point.y()-self.tolerance,point.x()+self.tolerance,point.y()+self.tolerance)
		
	def doIntersection(self, initPoint, observations):
		nObs = len(observations)
		if nObs<2: return
		if nObs==2:
			intersectedPoint = self.twoCirclesIntersect(observations, initPoint)
			if intersectedPoint is None:return
			if self.settings.value("intersecResultConfirm"):
				reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "A perfect intersection has been found using two circles. Use this solution?", QMessageBox.Yes, QMessageBox.No )			
				if reply == QMessageBox.No:	return
		else:
			intersectedPoint,report = self.leastSquares(observations, initPoint)
			if self.settings.value("intersecResultConfirm"):
				if not LSreport(report).exec_(): return
		
		# save the intersection result (point) and its report
		while True:
			if not self.settings.value("intersecResultPlacePoint"): break # if we do not place any point, skip
			intLayer = next( ( layer for layer in self.iface.mapCanvas().layers() if layer.id() == self.settings.value("intersectionLayer") ), None )
			if intLayer is None:
				reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "To place the intersection solution, you must select a layer in the settings. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
				if reply == QMessageBox.No:	        return
				if self.uisettings.exec_() ==	 0: return
				continue
			if self.settings.value("intersecResultPlaceReport"): 
				reportField = next( ( field for field in intLayer.dataProvider().fieldNameMap() if field == self.settings.value("reportField") ), None )
				if reportField is None:
					ok = False
					reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "To save the intersection report, please select a field for tit. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
					if reply == QMessageBox.No:  	 return
					if self.uisettings.exec_() == 0: return
					continue
			break
		if self.settings.value("intersecResultPlacePoint"):
			f = QgsFeature()
			f.setGeometry(QgsGeometry.fromPoint(intersectedPoint))
			if self.settings.value("intersecResultPlaceReport"): 
				irep = intLayer.dataProvider().fieldNameIndex(reportField)
				f.addAttribute(irep,QVariant(report))
			intLayer.dataProvider().addFeatures( [f] )
			intLayer.updateExtents()
			self.canvas.refresh()
			
		# check that dimension layer and fields have been set correctly
		while True:
			if not self.settings.value("dimenPlaceDimension"): return # if we do not place any dimension, skip
			dimLayer = next( ( layer for layer in self.iface.mapCanvas().layers() if layer.id() == self.settings.value("dimensionLayer") ), None )
			if dimLayer is None:
				reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "To place dimension arcs, you must select a layer in the settings. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
				if reply == QMessageBox.No:	        return
				if self.uisettings.exec_() ==	 0: return
				continue
			if self.settings.value("dimenPlaceMeasure"): 
				measureField = next( ( True for field in dimLayer.dataProvider().fieldNameMap() if field == self.settings.value("measureField") ), None )
				if measureField is None:
					ok = False
					reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "To save the measured distance, please select a field for tit. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
					if reply == QMessageBox.No:  	 return
					if self.uisettings.exec_() == 0: return
					continue
			if self.settings.value("dimenPlacePrecision"): 
				precisionField = next( ( True for field in dimLayer.dataProvider().fieldNameMap() if field == self.settings.value("precisionField") ), None )
				if precisionField is None:
					ok = False
					reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "To save the measure precision, please select a field for it. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
					if reply == QMessageBox.No: 	 return
					if self.uisettings.exec_() == 0: return
					continue
			break
		dlg = PlaceDimension(self.iface,intersectedPoint,observations,[self.lineLayer(),self.pointLayer()])
		dlg.exec_()	
		
	def leastSquares(self, observations, initPoint):
		threshold = self.settings.value("intersecLSconvergeThreshold")
		# initial parameters
		x0  = np.array( [ [initPoint.x()] , [initPoint.y()] ] ) # brackets needed to create column and not row vector
		report = "Initial position: %13.3f %13.3f\n" % (x0[0],x0[1])
		dx =  np.array( [ [2*threshold],[2*threshold] ] )
		it = 0
		# global observations vector
		l = np.array( [ [obs["measure"]] for obs in observations] ) # brackets needed to create column and not row vector
		# adjustment main loop
		while max(np.abs(dx))>threshold:
			it += 1
			if it > self.settings.value("intersecLSmaxIter"):
				x0 = [None,None]
				report += "\n!!! Maximum iterations reached (%u)" % (it-1)
				break
			# init matrices
			A   = []
			B   = []
			Qll = []
			w   = []
			for i,obs in enumerate(observations):
				if obs["type"] == "distance":
					# distance equation: (x - xc)^2 + (y-yc)^2 - l^2 = 0 (obs: r, param: xc,yc, fixed: x,y)
					# jacobian for parameters
					A.append( [2*x0[0][0]-2*obs["x"] , 2*x0[1][0]-2*obs["y"]] )
					# jacobian for observations
					B.append(-2*obs["measure"])
					# stochastic model
					Qll.append( math.pow(obs["precision"]/1000,2))
					# misclosure
					w.append( [ math.pow(x0[0]-obs["x"],2) + math.pow(x0[1]-obs["y"],2) - math.pow(obs["measure"],2) ] ) # brackets needed to create column and not row vector
			# generate matrices
			A   = np.array( A   )
			B   = np.diag(  B   )
			Qll = np.diag(  Qll )
			w   = np.array(  w  )		
			# weight matrix
			Pm  = np.dot( B , np.dot(Qll,B.T) )
			P   = la.inv( Pm )
			# normal matrix
			N   = np.dot( A.T , np.dot(P,A) )
			u   = np.dot( A.T , np.dot(P,w) )
			# QR decomposition
			q,r = la.qr(N)
			p   = np.dot(q.T,u)
			dx  = np.dot(la.inv(r),p)
			x0 -= dx
			report += "\nCorrection %u: %10.4f %10.4f" % (it,dx[0],dx[1])
		Qxx = la.inv(N)
		p1 = math.sqrt(Qxx[0][0])
		p2 = math.sqrt(Qxx[1][1])
		# residuals -Qll*B'*( P * (A* dx(iN)+w) ) !!! ToBeChecked !!!
		v = np.dot( -Qll , np.dot( B.T , np.dot( P , np.dot( A,dx) + w ) ) )
		report += "\n"
		report += "\nSolution:\t%13.3f\t%13.3f" % (x0[0],x0[1])
		report += "\nPrecision:\t%13.3f\t%13.3f" % (p1,p2)
		report += "\n\n Observation  |       x       |       y       |   Measure   | Precision | Residual"
		report +=   "\n              |  [map units]  |  [map units]  | [map units] |  [1/1000] | [1/1000]"
		for i,obs in enumerate(self.observations):
			report += "\n%13s | %13.3f | %13.3f | %11.3f | %9.1f | %7.1f" % (obs["type"],obs["x"],obs["y"],obs["measure"],obs["precision"],1000*v[i][0])
		sigmapos =  np.dot( v.T , np.dot( P , v ) ) / (self.nObs -2 ) # vTPv / r
		if sigmapos > 1.8: sigmapos_comment = "precision is too optimistic"
		elif sigmapos < .5: sigmapos_comment = "precision is too pessimistc"
		else: sigmapos_comment = "precision seems realistic"
		report += "\n\nSigma a posteriori: %5.2f \t (%s)" % (sigmapos,sigmapos_comment)
		return QgsPoint(x0[0],x0[1]) , report

	def twoCirclesIntersect(self, observations, initPoint):
		# see http://www.mathpages.com/home/kmath396/kmath396.htm
		x1 = observations[0]["x"]
		y1 = observations[0]["y"]
		r1 = observations[0]["measure"]
		x2 = observations[1]["x"]
		y2 = observations[1]["y"]
		r2 = observations[1]["measure"]
		d = math.sqrt( math.pow(x1-x2,2) + math.pow(y1-y2,2) )
		if d<math.fabs(r1-r2):
			# circle is within the other
			return None
		if d>r1+r2:
			# circles are not intersecting, scaling their radius to get intersection"
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
		pt1 = QgsPoint(xa,ya)
		pt2 = QgsPoint(xb,yb)
		# return unique point
		d1 = pt1.sqrDist(initPoint)
		d2 = pt2.sqrDist(initPoint)
		if d1<d2: return pt1
		else:     return pt2
