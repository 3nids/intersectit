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
    return "Version 1.0.3"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.7"
def classFactory(iface):
    from intersectit import intersectit
    return intersectit(iface)
    




