
### 3.5.6 26.09.2017

* fix several release issues

### 3.5.5 07.09.2017

* fix bad release

### 3.5.4 07.09.2017

* fix python crash

### 3.5.3 08.06.2016

* fix advanced intersection map tool (missing import)

### 3.5.2 04.05.2016

* fix creating layer on startup

### 3.5.1 03.05.2016

* use new snapping API (part 2)
* use new legend API

### 3.5 02.05.2016

* use new snapping API (QGIS min 2.8)
* improved handling of the settings

### 3.4.2 23.10.2014

* added spanish translation (thanks to Lucas Alonso)

### 3.4.1 17.03.2014

* fix API break in QGIS 2.3

### 3.4 21.02.2014

* perform all possible intersections in simple intersection, return the closest one
* added colored icons

### 3.3.1 12.12.2013

* remove intersection solution from rubber band
* completed frend translation
* fix python crash when editing orientations

### 3.3 02.12.2013

* use distinct layers for orientation and distance dimensions

### 3.2.1 11.09.2013

* use correct settings for rubber band

### 3.2 22.08.2013

* only use visible layers for snapping
* display snapped layers if simple intersection fails
* fix set rubber bands style

### 3.1 15.08.2013

* Define icon for snapping
* Allow alpha channel in rubber band color

### 3.0 07.08.2013 _experimental_

* Distance
    * display snap info in the message bar
    * correctly remove rubber band if canceling
    * fix crash if layer removed while map tool is active
* Intersection (now called advanced)
    * prevent intersection from only one element
    * add solution in rubber band
    * fix intersection distance / orientation
* Simple intersection
    * new tool to intersect exactly 2 line or polygon features from any layer and write intersection to a point layer
* Dimensions
    * now use a standard linestring for dimensions
    * tool to edit arcs for dimensions of distances (like in cadtools plugin)
* General settings for snapping and rubbers bands
* Added French translation

### 2.0 01.07.2013 _experimental_

* Added prolongation/angles to possible observations
* General interface for intersection:
    * add/remove observation
    * edit precision of obsevations
    * validate results
* updated to new API

### 1.0.3 26.03.2012
* Increased max length for distances to 999km

### 1.0.2 23.03.2012
* Added one digit in place distance UI

###1.0.1 21.03.2012
* Added help in menu
