import processing, os, glob
from osgeo import gdal, osr
###PARAMETERS
# INPUT PATH FOR MNT TO MOSAIC AND ANALYZE
dtm_path = ""
# PATH FOR OUTPUT FILES
output_path = ""
# PATH AND NAME OF SLD FILE
style = output_path + "Aspect_Slope_Style.qml"
# RASTER TYPE TO FETCH
types = ('*.jpg', '*.asc', '*.tif', '*.png')
# COORDINATE REFERENCE SYSTEM
crs=

### CREATION OF ASPECT (DEGREES) AND SLOPE (POURCENT) CLASSIFICATION TEXT
# ASPECT
aspect_reclass_txt = output_path + "aspect_reclass.txt"
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
faspect = open(aspect_reclass_txt, "w")
faspect.writelines(aspect)
faspect.close()
# SLOPE
slope_reclass_txt = output_path + "slope_reclass.txt"
slope = [
    "0.0 thru 4.999 = 0 \n",
    "5.0 thru 9.999 = 2 \n",
    "10.0 thru 19.999 = 4 \n",
    "20.0 thru 44.999 = 6 \n",
    "45.0 thru 100.0 = 8 \n"
]
fslope = open(slope_reclass_txt, "w")
fslope.writelines(slope)
fslope.close()

### PROCESSING START
# FETCHING ALL RASTER IN INPUT PATH
files_grabbed = []
crs= str (crs)
os.chdir(dtm_path + '/')
for raster in types:
    files_grabbed.extend(glob.glob(dtm_path+raster))
    print(files_grabbed)
for raster in files_grabbed:
    processing.run("gdal:assignprojection", {'INPUT':raster,'CRS':QgsCoordinateReferenceSystem('EPSG:'+crs)})
layer_name_mosaic = 'mosaic'
mosaic = output_path + layer_name_mosaic +".sdat"
processing.run("saga:mosaicrasterlayers", {
    'GRIDS':files_grabbed,
    'NAME':'Mosaic',
    'TYPE':7,
    'RESAMPLING':0,
    'OVERLAP':1,
    'BLEND_DIST':10,
    'MATCH':0,
    'TARGET_USER_XMIN TARGET_USER_XMAX TARGET_USER_YMIN TARGET_USER_YMAX':None,
    'TARGET_USER_SIZE':5,
    'TARGET_USER_FITS':1,
    'TARGET_OUT_GRID':mosaic
})
processing.run("gdal:assignprojection", {'INPUT':mosaic,'CRS':QgsCoordinateReferenceSystem('EPSG:'+crs)})
mosaic_layer = iface.addRasterLayer(mosaic, '')

# CREATION OF ASPECT AND SLOPE STYLE
slope = output_path + 'intensity_slope' + '.tif'
aspect = output_path + 'aspect_slope' + '.tif'
processing.run("grass7:r.slope.aspect", {
  'elevation':mosaic,
  'format':1,
  'precision':0,
  '-a':True,
  '-e':False,
  '-n':False,
  'zscale':1,
  'min_slope':0,
  'slope':slope,
  'aspect':aspect,
  'GRASS_REGION_PARAMETER':None,
  'GRASS_REGION_CELLSIZE_PARAMETER':0,
  'GRASS_RASTER_FORMAT_OPT':'',
  'GRASS_RASTER_FORMAT_META':''
})
processing.run("gdal:assignprojection", {'INPUT':slope,'CRS':QgsCoordinateReferenceSystem('EPSG:'+crs)})
processing.run("gdal:assignprojection", {'INPUT':aspect,'CRS':QgsCoordinateReferenceSystem('EPSG:'+crs)})
slope_layer = iface.addRasterLayer(slope, '')
aspect_layer = iface.addRasterLayer(aspect, '')

# CLASSIFICATION WITH TXT FILES
slope_reclass = output_path + 'intensity_slope_reclass' + '.tif'
aspect_reclass = output_path + 'aspect_slope_reclass' + '.tif'
processing.run("grass7:r.reclass", {
  'input':aspect,
  'rules':aspect_reclass_txt,
  'txtrules':'',
  'output':aspect_reclass,
  'GRASS_REGION_PARAMETER':None,
  'GRASS_REGION_CELLSIZE_PARAMETER':0,
  'GRASS_RASTER_FORMAT_OPT':'',
  'GRASS_RASTER_FORMAT_META':''
})
processing.run("grass7:r.reclass", {
  'input':slope,
  'rules':slope_reclass_txt,
  'txtrules':'',
  'output':slope_reclass,
  'GRASS_REGION_PARAMETER':None,
  'GRASS_REGION_CELLSIZE_PARAMETER':0,
  'GRASS_RASTER_FORMAT_OPT':'',
  'GRASS_RASTER_FORMAT_META':''
})
processing.run("gdal:assignprojection", {'INPUT':slope_reclass,'CRS':QgsCoordinateReferenceSystem('EPSG:'+crs)})
processing.run("gdal:assignprojection", {'INPUT':aspect_reclass,'CRS':QgsCoordinateReferenceSystem('EPSG:'+crs)})
slope_reclass_layer = iface.addRasterLayer(slope_reclass, '')
aspect_reclass_layer = iface.addRasterLayer(aspect_reclass, '')

# RASTER CALCULATOR TO ADD BOTH RASTERS
add_intensity_aspect = output_path + 'add_intensity_aspect' + '.tif'
processing.run("grass7:r.mapcalc.simple", {
  'a':aspect_reclass,
  'b':slope_reclass,
  'c':None,'d':None,'e':None,'f':None,
  'expression':'A+B',
  'output':add_intensity_aspect,
  'GRASS_REGION_PARAMETER':None,
  'GRASS_REGION_CELLSIZE_PARAMETER':0,
  'GRASS_RASTER_FORMAT_OPT':'',
  'GRASS_RASTER_FORMAT_META':''
})
processing.run("gdal:assignprojection", {'INPUT':add_intensity_aspect,'CRS':QgsCoordinateReferenceSystem('EPSG:'+crs)})
add_intensity_aspect_layer = iface.addRasterLayer(add_intensity_aspect, '')

# LOAD STYLE
add_intensity_aspect_layer.loadNamedStyle(style)
add_intensity_aspect_layer.triggerRepaint()
