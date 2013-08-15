## What?

Intersect It is a QGIS plugin to construct points by intersecting distances and orientations and to draw dimensions.

This plugin requires numpy if you want to use the advanced intersection which is solved using least-squares adjustment.

## How ?

### Observations

First, you have to place observations which can be **distance** or **orientation**.
Click on the corresponding icon to place an observation.

In the plugin settings, you can define the snapping behavior.

The observations are put in two memory layers which are automatically created by the plugin (_IntersectIt Points_ and _IntersectIt Lines_).

The observations can be deleted using the standard tools from QGIS or all at once using the eraser icon.

### Intersection

Once you have place the needed observations, you may want to intersect them Two tools are offered:

* **simple intersection**: it will allow the instersection of two linear (also polygonal) objects from any layer in the legend. A point will be created at the intersection in the chosen layer (settings).
* **advanced intersection**: this tool can be used to intersect 2 or more observations (distance or observations) using a least-square adjustment. Once finished, it will also create dimension for each observation.

### Dimensions

Once the advanced intersection is found, if defined in settings, the dimensions will be written in chosen layer.
Arcs are drawn for distance and lines are drawn for orientations.
They can be edited using the corresponding icons.

