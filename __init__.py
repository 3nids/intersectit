"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012
"""
def name():
    return "Triangulation"
def description():
    return "Allows determination of a position based on distance to points. If the problem is over-determined, a weighted least-squares solution is returned."
def version():
    return "Version 0.1"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.7"
def classFactory(iface):
    from triangulation import triangulation
    return triangulation(iface)
    




