# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 12:34:24 2022

@author: kyles
"""

import arcpy, sys
import math
from arcpy import env
from arcpy.sa import *
import pandas as pd
import numpy as np
from arcpy import sa
from arcpy.sa import *

path = sys.path[0]
arcpy.env.workspace = path


wolf_range = 'usfws_A00D_V16_Canis_lupus_current_range\usfws_A00D_V16_Canis_lupus_current_range.shp'
raster = 'land_cover\nlcd_2019_land_cover_l48_20210604.tif' #manually change raster back to this in variable explorer

env.overwriteOutput = 1

env.outputCoordinateSystem = arcpy.Describe(raster).spatialReference

#convert nlcd layer from img to tiff format
#Run time: 23 minutes 35 seconds
arcpy.RasterToOtherFormat_conversion('nlcd_2019_land_cover_l48_20210604/nlcd_2019_land_cover_l48_20210604.img', 
                                     arcpy.env.workspace+'\land_cover','TIFF')


#clip nlcd raster to wolf habitat
arcpy.Clip_management(raster,'-1937750.541096 2026761.618524 -594903.892581 3101752.738209',
                      'land_cover\clipped_raster.tif',wolf_range,'0','ClippingGeometry','NO_MAINTAIN_EXTENT')

##points code 
df = pd.read_csv(arcpy.env.workspace+'\observations-226409.csv\observations-226409.csv')

latitude = df['latitude'].values
longitude = df['longitude'].values    

coords = list(map(lambda x,y: (x,y),longitude,latitude))

arcpy.CreateFeatureclass_management(arcpy.env.workspace+'\wolf_sightings_points','wolf_sightings.shp','POINT')
proj = arcpy.SpatialReference('WGS 1984')
arcpy.DefineProjection_management('wolf_sightings_points\wolf_sightings.shp', proj)

point = arcpy.Point()    
    
with arcpy.da.InsertCursor('wolf_sightings_points\wolf_sightings.shp','SHAPE@') as cursor:
    for coord in coords:
        point.X = coord[0]
        point.Y = coord[1]
        cursor.insertRow([point])

arcpy.Project_management('wolf_sightings_points\wolf_sightings.shp', 
  
                         'wolf_sightings_points\wolf_sightings_project.shp', env.outputCoordinateSystem)

##make wolf range raster

#clip points to overall wolf range
arcpy.Clip_analysis('wolf_sightings_points\wolf_sightings_project.shp',wolf_range,
                      'wolf_sightings_points\wolf_sightings_clipped.shp')

#buffer clipped wolf points
arcpy.analysis.Buffer('wolf_sightings_points\wolf_sightings_clipped.shp', 
                      'wolf_sightings_points\wolf_sightings_buffer.shp', '50 miles')

#clip buffer points to fit within the raster
arcpy.Clip_analysis('wolf_sightings_points\wolf_sightings_buffer.shp',wolf_range,
                      'wolf_sightings_points\wolf_sightings_buffer_clipped.shp')

#dissolve buffers
arcpy.management.Dissolve('wolf_sightings_points\wolf_sightings_buffer_clipped.shp',
                          'wolf_sightings_points\wolf_sightings_buffer_dissolved.shp')

#clip wolf raster to dissolved buffered wolf sighting points
arcpy.Clip_management('land_cover\clipped_raster.tif','-1810953.529540 2131909.442026 -971067.310480 3095636.203192',
                      'land_cover\wolf_range_raster.tif','wolf_sightings_points\wolf_sightings_buffer_dissolved.shp',
                      '0','ClippingGeometry','NO_MAINTAIN_EXTENT')

#split raster
arcpy.SplitRaster_management('land_cover\wolf_range_raster.tif', 'land_cover\split_raster', 'ras', 
                             'NUMBER_OF_TILES','TIFF', '#', '20 20')
    
## raster anlysis
                         
#set workspace to location of split rasters
arcpy.env.workspace = r'C:\Users\kyles\Documents\GEOG4303\Project\land_cover\split_raster' 

#get list of split raster file names
files = arcpy.ListFiles('*.TIF')

#nlcd values
nlcd_values = [11,12,31,41,42,43,51,52,71,72,73,74,90,95]

#intialize nlcd_count dictionary
nlcd_counts = {}
for value in nlcd_values:
    nlcd_counts[value] = 0

total_values = 0

for f in files:
    demRaster = sa.Raster(f)
    demArray = arcpy.RasterToNumPyArray(demRaster)
    
    for value in nlcd_values:
        count = len(np.where(demArray == value)[0])
        nlcd_counts[value] += count
        total_values += count
    
#make nlcd_means dictionary
nlcd_means = {}
for value in nlcd_values:
    nlcd_means[value] = float(nlcd_counts[value])/float(total_values)

print(nlcd_means)

#make nlcd_criteria dict
nlcd_criteria = {42: 0.3948653265293449-0.1, 52: 0.3765858617013522-0.1}


##create colorado nlcd layer
arcpy.env.workspace = r'C:\Users\kyles\Documents\GEOG4303\Project' #reset workspace

state_boundries = 'state_boundries\state_boundries.shp'

arcpy.Project_management(state_boundries,'state_boundries\state_boundries_project.shp',env.outputCoordinateSystem)

state_boundries_project = 'state_boundries\state_boundries_project.shp'

#get Colorado state boundry
sql_clause = '"NAME" = \'Colorado\''
arcpy.Select_analysis(state_boundries_project, 'state_boundries\colorado.shp', sql_clause)

#get colorado raster
colorado =  'state_boundries\colorado.shp'
arcpy.Clip_management(raster,'-1218951.524318 1504008.955420 -474143.581768 2140044.824831',
                      'land_cover\colorado_raster.tif',colorado,'0','ClippingGeometry','NO_MAINTAIN_EXTENT')

                             
##raster analysis of colorado
                             
#split colorado raster
arcpy.SplitRaster_management('land_cover\colorado_raster.tif', 'land_cover\split_raster_colorado', 'rass', 
                             'NUMBER_OF_TILES','TIFF', '#', '10 10')
                             
arcpy.env.workspace = r'C:\Users\kyles\Documents\GEOG4303\Project\land_cover\split_raster_colorado' 

files = arcpy.ListFiles('*.TIF')

candidate_rasters = []

#see if each split raster meets criteria
#if yes then add to list of candidate rasters
for f in files:
    demRaster = sa.Raster(f)
    demArray = arcpy.RasterToNumPyArray(demRaster)
    
    size = len(np.where(demArray != 0)[0])
    
    condition_count = 0
    for key in nlcd_criteria.keys():
        percentage = float(len(np.where(demArray == key)[0]))/float(size)
        if percentage >= nlcd_criteria[key]:
            condition_count += 1
    if condition_count > 0:
        candidate_rasters.append(f)
        
print(candidate_rasters)

#use Mosaic To New Raster to make final composite raster
arcpy.MosaicToNewRaster_management(candidate_rasters,arcpy.env.workspace,'composite_raster.tif','#','#','#','1')
      
