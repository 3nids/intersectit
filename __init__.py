"""
Intersect It QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
March. 2012
"""
def name():
    return "Intersect It"
def description():
    return "Intersect It is a QGIS plugin to place measures (distance or orientation) with their corresponding precision, intersect them using a least-squares solution and save dimensions in a dedicated layer to produce maps."
def version():
    return "Version 2.0"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.9"
def classFactory(iface):
    from intersectit import IntersectIt
    return IntersectIt(iface)
    




