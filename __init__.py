"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012
"""
def name():
    return "Intersect It"
def description():
    return "Place measures with their corresponding precision, intersect the measures using a least-squares solution and place dimensions in layers to keep the measures available on maps."
def version():
    return "Version 0.1"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.7"
def classFactory(iface):
    from intersectit import intersectit
    return intersectit(iface)
    




