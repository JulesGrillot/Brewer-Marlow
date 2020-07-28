# Brewer & Marlow

QGIS3 Processing Chain to analyze DTM with slope and aspect.


<img src="/map_example.png" ></img>

# Data needed for this operation

 - DTM
 - Style file
 
 # First Step
 
  Fetch the DTM in the input path, check their projection and then mosaic them. 
  The script is using : 
    - gdal tool "assign projection".
    - saga tool "mosaic raster layers"
 
 # Second Step
  
  Use the Mosaic to create two rasters :
    - a raster for slopes
    - a raster for aspect
    
  The script is using grass tool "r.slope.aspect"
  
 # Thirs Step
  
   Those rasters need to be reclassified.
   We need to create rules for each raster. Those rules can be changed if needed.
   
```python
aspect = [
    "0.0 thru 22.499 = 10 \n",
    "22.5 thru 67.499 = 20 \n",
    "67.5 thru 112.499 = 30 \n",
    "112.5 thru 157.499 = 40 \n",
    "157.5 thru 202.499 = 50 \n",
    "202.5 thru 247.499 = 60 \n",
    "247.5 thru 292.499 = 70 \n",
    "292.5 thru 337.499 = 80 \n",
    "337.5 thru 360.5 = 10 \n"
]
```

```python
slope = [
    "0.0 thru 4.999 = 0 \n",
    "5.0 thru 9.999 = 2 \n",
    "10.0 thru 19.999 = 4 \n",
    "20.0 thru 44.999 = 6 \n",
    "45.0 thru 100.0 = 8 \n"
]
```
  We can now launch the reclassification using grass tool "r.reclass".
  
 # Fourth Step
   
   Combine the rasters to make one file. Every pixel have a value between 10 and 88. 
   The tens digit indicates the aspect, a number represent an angle of 45°.
   The units digit indicates the slope :
    - 0 : gentle slope
    - 2 : moderate slope
    - 4 : strong slope
    - 6 : very strong slope
    - 8 : steep slope
   
   The script is using grass tool "r.mapcalc.simple".
   Once the raster is created we add the style.
  

Processing Chain based on this article by Jon Reades :
https://kingsgeocomputation.org/2016/03/16/aspect-slope-maps-in-qgis/
