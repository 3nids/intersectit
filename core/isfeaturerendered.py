#-----------------------------------------------------------
#
# Intersect It is a QGIS plugin to place observations (distance or orientation)
# with their corresponding precision, intersect them using a least-squares solution
# and save dimensions in a dedicated layer to produce maps.
#
# Copyright    : (C) 2013 Denis Rouzaud
# Email        : denis.rouzaud@gmail.com
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this progsram; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------


from qgis.core import QgsRenderContext, QGis


def isFeatureRendered(canvas, layer, feature):
    renderer = layer.rendererV2()

    renderContext = QgsRenderContext()
    renderContext.setExtent(canvas.mapRenderer().rendererContext().extent())
    renderContext.setMapToPixel(canvas.mapRenderer().rendererContext().mapToPixel())
    renderContext.setRendererScale(canvas.mapRenderer().scale())

    if QGis.QGIS_VERSION_INT >= 20300:
        renderer.startRender(renderContext, layer.pendingFields())
    else:
        renderer.startRender(renderContext, layer)

    ans = renderer.willRenderFeature(feature)

    renderer.stopRender(renderContext)

    return ans
