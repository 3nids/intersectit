"""
Intersect It QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
March. 2012
"""


def classFactory(iface):
    from intersectit import IntersectIt
    return IntersectIt(iface)
    




